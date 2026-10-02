"""Client of the restricted Unix socket; never connects to Docker itself."""
import http.client
import json
import os
import socket
from urllib.parse import urlencode


class UnixHTTP(http.client.HTTPConnection):
    def __init__(self, path):
        super().__init__('localhost', timeout=15)
        self.path = path

    def connect(self):
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.settimeout(self.timeout)
        self.sock.connect(self.path)


class DockerReader:
    def __init__(self, path=None):
        self.path = path or os.getenv('GATEWAY_SOCKET', '/ipc/docker-read.sock')

    def get(self, route):
        conn = UnixHTTP(self.path)
        try:
            conn.request('GET', route)
            response = conn.getresponse()
            if response.status != 200:
                raise OSError('Restricted Docker reader unavailable')
            return json.load(response)
        except (ValueError, http.client.HTTPException) as exc:
            raise OSError('Invalid reader response') from exc
        finally:
            conn.close()

    def logs(self, since, until):
        return self.get('/logs?' + urlencode({'since': since, 'until': until}))['logs']

    def status(self):
        return self.get('/status')
