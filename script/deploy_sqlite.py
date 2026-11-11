"""SQLite snapshots and offline restoration for the dev deployment.

The caller MUST stop every writer before restore; this helper does not stop services.
"""

import argparse
from contextlib import closing
import os
from pathlib import Path
import sqlite3
import tempfile


def check_database(path):
    """Reject unreadable or corrupt snapshots without creating a missing database."""
    with closing(sqlite3.connect(Path(path).resolve().as_uri() + "?mode=ro", uri=True)) as db:
        if db.execute("PRAGMA integrity_check").fetchall() != [("ok",)]:
            raise RuntimeError("SQLite integrity_check failed")


def snapshot(source, destination):
    """Copy committed data, including WAL, to a standalone verified SQLite file."""
    source, destination = Path(source), Path(destination)
    if source.resolve() == destination.resolve():
        raise ValueError("Source and destination must differ")
    handle, temporary = tempfile.mkstemp(prefix=".sqlite-", dir=destination.parent)
    os.close(handle)
    try:
        with closing(sqlite3.connect(source.resolve().as_uri() + "?mode=ro", uri=True)) as src:
            with closing(sqlite3.connect(temporary)) as dst:
                src.backup(dst)
                dst.execute("PRAGMA journal_mode=DELETE")
        check_database(temporary)
        with open(temporary, "rb") as stream:
            os.fsync(stream.fileno())
        os.replace(temporary, destination)
        directory = os.open(destination.parent, os.O_RDONLY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def restore(source, destination):
    """Restore a snapshot atomically with writers stopped, discarding stale sidecars."""
    source, destination = Path(source), Path(destination)
    if source.resolve() == destination.resolve():
        raise ValueError("Source and destination must differ")
    metadata = destination.stat()
    # Validate the new file before touching either active data or its sidecars.
    handle, staged = tempfile.mkstemp(prefix=".restore-", dir=destination.parent)
    os.close(handle)
    try:
        snapshot(source, staged)
        os.chmod(staged, metadata.st_mode & 0o777)
        os.chown(staged, metadata.st_uid, metadata.st_gid)
        for suffix in ("-wal", "-shm", "-journal"):
            sidecar = Path(str(destination) + suffix)
            if sidecar.exists():
                sidecar.unlink()
        os.replace(staged, destination)
        directory = os.open(destination.parent, os.O_RDONLY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
        check_database(destination)
    finally:
        if os.path.exists(staged):
            os.unlink(staged)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("snapshot", "restore"))
    parser.add_argument("source")
    parser.add_argument("destination")
    args = parser.parse_args()
    {"snapshot": snapshot, "restore": restore}[args.action](args.source, args.destination)
