"""Fixed-target, read-only facade. This process alone holds the Docker socket."""
import argparse
from datetime import datetime
import http.client
from http.server import BaseHTTPRequestHandler
import json
import os
from pathlib import Path
import socket
from socketserver import UnixStreamServer
import struct
from urllib.parse import parse_qs, quote, urlencode, urlsplit

LIMIT = 32 * 1024 * 1024


class UnixHTTP(http.client.HTTPConnection):
    def __init__(self, path, timeout=10):
        super().__init__('localhost', timeout=timeout)
        self.path = path

    def connect(self):
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.settimeout(self.timeout)
        self.sock.connect(self.path)


def docker_read(socket_path, target, operation, params=None):
    """Build the Docker route internally; no caller-controlled Docker path."""
    route = '/v1.41/containers/' + quote(target, safe='') + '/' + operation
    if params:
        route += '?' + urlencode(params)
    client = UnixHTTP(socket_path)
    try:
        client.request('GET', route)
        response = client.getresponse()
        payload = response.read(LIMIT + 1)
        if response.status != 200 or len(payload) > LIMIT:
            raise OSError('Docker read unavailable')
        return payload
    finally:
        client.close()


def decode_logs(payload):
    if len(payload) < 8 or payload[0] not in (1, 2) or payload[1:4] != b'\x00\x00\x00':
        return payload.decode('utf-8', errors='replace')
    parts = []
    offset = 0
    while offset < len(payload):
        if len(payload) - offset < 8 or payload[offset] not in (1, 2) or payload[offset+1:offset+4] != b'\x00\x00\x00':
            raise ValueError('Invalid Docker log frame')
        size = struct.unpack('>I', payload[offset+4:offset+8])[0]
        if len(payload) - offset < size + 8:
            raise ValueError('Truncated Docker log frame')
        parts.append(payload[offset+8:offset+8+size])
        offset += size + 8
    return b''.join(parts).decode('utf-8', errors='replace')


class Handler(BaseHTTPRequestHandler):
    def setup(self):
        self.request.settimeout(5)
        super().setup()

    def log_message(self, *_):
        pass

    def reply(self, status, payload):
        data = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)
        self.close_connection = True

    def do_GET(self):
        route = urlsplit(self.path)
        try:
            if route.path == '/status' and not route.query:
                data = json.loads(docker_read(self.server.docker_socket, self.server.target, 'json'))
                state = data['State']
                self.reply(200, {'running': bool(state['Running']), 'status': state['Status'], 'health': state.get('Health', {}).get('Status', 'unknown')})
            elif route.path == '/logs':
                args = parse_qs(route.query, strict_parsing=True, keep_blank_values=True)
                if set(args) != {'since', 'until'} or any(len(v) != 1 for v in args.values()):
                    raise ValueError('Invalid parameters')
                since, until = args['since'][0], args['until'][0]
                times = [datetime.fromisoformat(v.replace('Z', '+00:00')) for v in (since, until)]
                if any(t.tzinfo is None for t in times) or times[1] < times[0] or (times[1] - times[0]).total_seconds() > 3600:
                    raise ValueError('Invalid log interval')
                payload = docker_read(self.server.docker_socket, self.server.target, 'logs', {'since': f'{times[0].timestamp():.6f}', 'until': f'{times[1].timestamp():.6f}', 'timestamps': 'true', 'stdout': 'true', 'stderr': 'true', 'follow': 'false'})
                self.reply(200, {'logs': decode_logs(payload)})
            else:
                self.reply(403, {'error': 'Forbidden'})
        except (ValueError, KeyError, TypeError):
            self.reply(400, {'error': 'Invalid request'})
        except (OSError, http.client.HTTPException):
            self.reply(503, {'error': 'Docker read unavailable'})

    def do_POST(self):
        self.reply(403, {'error': 'Forbidden'})

    do_DELETE = do_POST
    do_PUT = do_POST
    do_PATCH = do_POST
    do_HEAD = do_POST
    do_OPTIONS = do_POST


class Gateway(UnixStreamServer):
    def __init__(self, path, target, docker_socket='/var/run/docker.sock'):
        self.target, self.docker_socket = target, docker_socket
        super().__init__(path, Handler)
        os.chmod(path, 0o660)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--healthcheck', action='store_true')
    args = parser.parse_args()
    path = os.getenv('GATEWAY_SOCKET', '/ipc/docker-read.sock')
    if args.healthcheck:
        client = UnixHTTP(path)
        try:
            client.request('GET', '/status')
            raise SystemExit(0 if client.getresponse().status == 200 else 1)
        except OSError:
            raise SystemExit(1)
        finally:
            client.close()
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).unlink(missing_ok=True)
    with Gateway(path, os.environ['TARGET_CONTAINER']) as server:
        print('Docker gateway : fixed-target reads only', flush=True)
        server.serve_forever()


if __name__ == '__main__':
    main()
