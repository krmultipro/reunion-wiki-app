"""Read-only snapshot from the local machine; never uses the school VPS."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import time
from urllib import error, request


def snapshot():
    data = {'checked_at': datetime.now(timezone.utc).isoformat(), 'epoch': time.time()}
    try:
        with request.urlopen('https://reunionwiki.re/',timeout=15) as response:
            data['external_https'] = response.status
    except (OSError, error.URLError):
        data['external_https'] = None
    try:
        result = subprocess.run(['ssh','-o','BatchMode=yes','-o','ConnectTimeout=10','reunionwiki','docker exec telegram-logbot python /app/monitor.py --snapshot'],capture_output=True,text=True,timeout=30,check=True)
        data['monitor'] = json.loads(result.stdout)
    except (subprocess.SubprocessError, ValueError, OSError):
        data['monitor'] = None
    return data


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--record',action='store_true')
    args = parser.parse_args()
    data = snapshot()
    if args.record:
        target = Path(__file__).parent/'state'/'observation.jsonl'
        target.parent.mkdir(parents=True,exist_ok=True)
        with target.open('a') as stream:
            stream.write(json.dumps(data)+'\n')
        target.chmod(0o600)
    print(json.dumps(data))


if __name__ == '__main__':
    main()
