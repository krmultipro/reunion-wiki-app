"""Run the remote shell with fake Docker/HTTP commands, never a server or daemon."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]

DOCKER = r'''import json, os, pathlib, sys
args = sys.argv[1:]
trace = pathlib.Path(os.environ['MOCK_TRACE'])
with trace.open('a') as stream: stream.write(json.dumps([pathlib.Path(sys.argv[0]).name] + args) + '\n')
mode = os.getenv('MOCK_FAIL', '')
if pathlib.Path(sys.argv[0]).name == 'docker-compose':
    if 'up' in args and mode in ('candidate-up', 'restore', 'old-health'):
        entries = [json.loads(line) for line in trace.read_text().splitlines()]
        ups = sum(entry[0] == 'docker-compose' and 'up' in entry for entry in entries)
        if ups == 1: sys.exit(1)
    sys.exit(0)
if args[0] == 'inspect': print('sha256:old'); sys.exit(0)
if args[:2] == ['image', 'inspect']: print('170000000'); sys.exit(0)
if args[0] == 'run':
    if mode == 'tests' and 'python script/run_app_tests.py' in args[-1]: sys.exit(1)
    if 'snapshot' in args:
        volume = next(args[index+1] for index, arg in enumerate(args) if arg == '-v' and ':/backup' in args[index+1])
        if mode == 'final-snapshot' and '/db-backup:' in volume: sys.exit(1)
        pathlib.Path(volume.split(':')[0], 'base.db').write_bytes(b'snapshot')
    if 'restore' in args and mode == 'restore': sys.exit(1)
    if '-c' in args and 'iterdump' in args[-1]: print('same')
    if mode == 'source-sync' and 'cp -a /release/source/.' in args[-1]: sys.exit(1)
if args[:2] == ['exec', '-i'] and args[2] == 'web_dev' and mode == 'old-health': sys.exit(1)
'''


class RemoteDeploymentTests(unittest.TestCase):
    def run_deployment(self, failure=''):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        app = root / 'app'
        (app / 'data').mkdir(parents=True)
        (app / 'data/base.db').write_bytes(b'live')
        (app / '.env').touch()
        (app / 'docker-compose.yml').touch()
        deploy = root / 'deploy'
        release_name = '20261017T120000Z-123456abcdef'
        release = deploy / release_name
        release.mkdir(parents=True)
        source = root / 'source'
        (source / 'script').mkdir(parents=True)
        for filename in ('Dockerfile', 'migrate.py', 'script/deploy_smoke.py'):
            (source / filename).touch()
        archive = release / 'source.tar.gz'
        with tarfile.open(archive, 'w:gz') as tar:
            tar.add(source, arcname='.')
        script = root / 'deploy.sh'
        script.write_text((ROOT / 'script/deploy-dev-remote.sh').read_text().replace(
            'app_dir=/var/www/reunion-wiki-app-dev', 'app_dir=' + str(app)).replace(
            'deploy_root=/home/reunionwiki/deployments', 'deploy_root=' + str(deploy)))
        binary = root / 'bin'
        binary.mkdir()
        for command in ('docker', 'docker-compose'):
            executable = binary / command
            executable.write_text('#!' + sys.executable + '\n' + DOCKER)
            executable.chmod(0o755)
        curl = binary / 'curl'
        curl.write_text('#!/bin/sh\ncase "$*" in *https://dev.*) printf 401;; *) printf 200;; esac\n')
        curl.chmod(0o755)
        disk = binary / 'df'
        disk.write_text('#!/bin/sh\nprintf "Avail\\n"; if [ "$MOCK_FAIL" = disk ]; then printf "100\\n"; else printf "9999999999\\n"; fi\n')
        disk.chmod(0o755)
        trace = root / 'trace.jsonl'
        result = subprocess.run(['bash', str(script), release_name, '123456abcdef', hashlib.sha256(archive.read_bytes()).hexdigest()],
                                capture_output=True, text=True,
                                env={**os.environ, 'PATH': str(binary) + ':' + os.environ['PATH'],
                                     'MOCK_TRACE': str(trace), 'MOCK_FAIL': failure})
        entries = [json.loads(line) for line in trace.read_text().splitlines()] if trace.exists() else []
        return result, entries

    def test_snapshot_and_test_order_success(self):
        result, entries = self.run_deployment()
        self.assertEqual(result.returncode, 0, result.stderr)
        actions = [' '.join(entry) for entry in entries]
        tests = next(index for index, value in enumerate(actions) if 'python script/run_app_tests.py' in value)
        preliminary = next(index for index, value in enumerate(actions) if 'snapshot' in value)
        stop = next(index for index, value in enumerate(actions) if value == 'docker stop web_dev')
        final = next(index for index, value in enumerate(actions) if 'snapshot' in value and '/db-backup:' in value)
        switch = next(index for index, value in enumerate(actions) if 'docker tag reunion-wiki-app-dev_web:candidate-' in value)
        self.assertLess(tests, preliminary)
        self.assertLess(stop, final)
        self.assertLess(final, switch)
        self.assertIn('--network none', actions[tests])
        self.assertNotIn('--env-file', actions[tests])
        self.assertFalse(any(' restore ' in value for value in actions))

    def test_candidate_failure_restores_and_checks_old_service(self):
        result, entries = self.run_deployment('candidate-up')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Retour arrière contrôlé', result.stderr)
        actions = [' '.join(entry) for entry in entries]
        restored = next(index for index, value in enumerate(actions) if ' restore ' in value)
        old_tag = next(index for index, value in enumerate(actions) if 'docker tag reunion-wiki-app-dev_web:before-' in value)
        old_health = next(index for index, value in enumerate(actions) if 'docker exec -i web_dev python -' in value)
        self.assertLess(restored, old_tag)
        self.assertLess(old_tag, old_health)

    def test_restore_failure_never_restarts_old_service(self):
        result, entries = self.run_deployment('restore')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('ROLLBACK ÉCHOUÉ : restauration SQLite', result.stderr)
        self.assertNotIn('Retour arrière contrôlé', result.stderr)
        self.assertEqual(sum(entry[0] == 'docker-compose' and 'up' in entry for entry in entries), 1)

    def test_old_service_health_failure_is_explicit(self):
        result, _ = self.run_deployment('old-health')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('ROLLBACK ÉCHOUÉ : ancien service non validé', result.stderr)
        self.assertNotIn('Retour arrière contrôlé', result.stderr)

    def test_source_sync_failure_restores_previous_code(self):
        result, entries = self.run_deployment('source-sync')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Retour arrière contrôlé', result.stderr)
        self.assertTrue(any('tar -xzf /release/previous-source.tar.gz' in entry[-1] for entry in entries))

    def test_failed_image_tests_never_stop_or_switch_live_service(self):
        result, entries = self.run_deployment('tests')
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(any(entry[:3] == ['docker', 'stop', 'web_dev'] for entry in entries))
        self.assertFalse(any(entry[0] == 'docker-compose' and 'up' in entry for entry in entries))
        self.assertFalse(any('snapshot' in entry for entry in entries))

    def test_failed_final_snapshot_restarts_old_service_without_restoring_database(self):
        result, entries = self.run_deployment('final-snapshot')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('base initiale conservée', result.stderr)
        self.assertFalse(any('restore' in entry for entry in entries))
        self.assertEqual(sum(entry[0] == 'docker-compose' and 'up' in entry for entry in entries), 1)
        self.assertTrue(any(entry[:5] == ['docker', 'exec', '-i', 'web_dev', 'python'] for entry in entries))

    def test_preliminary_copy_uses_root_inside_container(self):
        result, entries = self.run_deployment()
        self.assertEqual(result.returncode, 0, result.stderr)
        copy = next(entry for entry in entries if 'cp /backup/base.db /data/base.db' in entry[-1])
        self.assertEqual(copy[copy.index('--user') + 1], '0:0')
        self.assertIn('chown -R appuser:appuser /data', copy[-1])

    def test_insufficient_capacity_stops_before_build_and_service_mutation(self):
        result, entries = self.run_deployment('disk')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('capacité disque insuffisante', result.stderr)
        self.assertFalse(any(entry[:2] == ['docker', 'build'] for entry in entries))
        self.assertFalse(any('stop' in entry or 'up' in entry for entry in entries))

    def test_final_snapshot_and_rollback_include_uploads_and_candidate_writes(self):
        result, entries = self.run_deployment('candidate-up')
        self.assertNotEqual(result.returncode, 0)
        actions = [' '.join(entry) for entry in entries]
        final = next(i for i, x in enumerate(actions) if 'deploy_data.py snapshot /source /backup/data' in x)
        recovery = next(i for i, x in enumerate(actions) if 'deploy_data.py snapshot /data /backup/failed-candidate' in x)
        restored = next(i for i, x in enumerate(actions) if 'deploy_data.py restore /backup/data /data' in x)
        self.assertLess(final, recovery)
        self.assertLess(recovery, restored)
