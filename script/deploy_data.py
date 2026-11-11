"""Private SQLite + uploads snapshots. Restore requires every writer stopped."""

import argparse
from contextlib import closing
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import sqlite3
import stat
import tempfile
import uuid

try:
    from .deploy_sqlite import snapshot, restore
except ImportError:
    from deploy_sqlite import snapshot, restore


def file_hash(path):
    """Return a streaming SHA-256 without exposing file contents."""
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def upload_inventory(root):
    """Describe regular upload files, rejecting links and special files."""
    root = Path(root)
    inventory = {}
    if root.is_symlink():
        raise ValueError("Upload root must not be a link")
    if not root.exists():
        return inventory
    if not root.is_dir():
        raise ValueError("Upload root must be a real directory")
    for path in sorted(root.rglob("*")):
        if path.is_symlink() or not (path.is_dir() or path.is_file()):
            raise ValueError("Upload links and special files are not supported")
        if path.is_file():
            metadata = path.stat()
            inventory[path.relative_to(root).as_posix()] = {
                "sha256": file_hash(path), "bytes": metadata.st_size,
                "mode": stat.S_IMODE(metadata.st_mode),
                "uid": metadata.st_uid, "gid": metadata.st_gid,
            }
    return inventory


def database_metadata(path):
    """Check a standalone database and summarize it without personal values."""
    with closing(sqlite3.connect(Path(path).resolve().as_uri() + "?mode=ro", uri=True)) as db:
        if db.execute("PRAGMA integrity_check").fetchall() != [("ok",)]:
            raise RuntimeError("SQLite integrity_check failed")
        tables = [row[0] for row in db.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
        counts = {name: db.execute('SELECT COUNT(*) FROM "' + name.replace('"', '""') + '"').fetchone()[0]
                  for name in tables}
        digest = hashlib.sha256("\n".join(db.iterdump()).encode()).hexdigest()
        return {"logical_sha256": digest, "table_counts": counts,
                "foreign_key_violations": len(db.execute("PRAGMA foreign_key_check").fetchall())}


def verify_bundle(bundle):
    """Verify DB integrity, counts and every stored upload against the manifest."""
    bundle = Path(bundle)
    manifest = json.loads((bundle / "manifest.json").read_text())
    if manifest.get("version") != 1:
        raise ValueError("Unsupported bundle manifest")
    if file_hash(bundle / "base.db") != manifest["database_sha256"]:
        raise RuntimeError("Database hash mismatch")
    if database_metadata(bundle / "base.db") != manifest["database"]:
        raise RuntimeError("Database metadata mismatch")
    files = upload_inventory(bundle / "uploads")
    expected = manifest["uploads"]
    if set(files) != set(expected) or any(
            files[name][key] != expected[name][key]
            for name in files for key in ("sha256", "bytes")):
        raise RuntimeError("Upload inventory mismatch")
    return manifest


def snapshot_bundle(source, destination):
    """Snapshot DB and uploads, refusing a bundle changed by concurrent writers."""
    source, destination = Path(source).resolve(), Path(destination).absolute()
    if destination.exists() or source == destination or source in destination.parents:
        raise ValueError("Snapshot destination must be new and outside active data")
    if (source / "base.db").is_symlink():
        raise ValueError("Database source must not be a link")
    destination.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    stage = Path(tempfile.mkdtemp(prefix=".snapshot-", dir=destination.parent))
    try:
        files_before = upload_inventory(source / "uploads")
        snapshot(source / "base.db", stage / "base.db")
        baseline = database_metadata(stage / "base.db")
        (stage / "uploads").mkdir(mode=0o700)
        for name in files_before:
            target = stage / "uploads" / name
            target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
            shutil.copyfile(source / "uploads" / name, target)
            target.chmod(0o600)
        # A second SQLite snapshot detects a write during the file-copy interval.
        snapshot(source / "base.db", stage / "check.db")
        if baseline != database_metadata(stage / "check.db") or files_before != upload_inventory(source / "uploads"):
            raise RuntimeError("Active data changed during snapshot; retry without writers")
        (stage / "check.db").unlink()
        manifest = {"version": 1, "created_at": datetime.now(timezone.utc).isoformat(),
                    "database_sha256": file_hash(stage / "base.db"),
                    "database": baseline, "uploads": files_before}
        (stage / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
        for path in stage.rglob("*"):
            path.chmod(0o700 if path.is_dir() else 0o600)
        verify_bundle(stage)
        stage.rename(destination)
        return manifest
    finally:
        if stage.exists():
            shutil.rmtree(stage)


def restore_bundle(bundle, destination):
    """Restore an offline DB and uploads, retaining displaced upload files."""
    bundle, destination = Path(bundle).resolve(), Path(destination).resolve()
    if bundle == destination or bundle in destination.parents or destination in bundle.parents:
        raise ValueError("Restore source must be outside active data")
    manifest = verify_bundle(bundle)
    if not (destination / "base.db").is_file():
        raise ValueError("Restore target database must already exist")
    stage = Path(tempfile.mkdtemp(prefix=".uploads-restore-", dir=destination))
    try:
        for name, metadata in manifest["uploads"].items():
            target = stage / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(bundle / "uploads" / name, target)
            target.chmod(metadata["mode"])
            if os.geteuid() == 0:
                os.chown(target, metadata["uid"], metadata["gid"])
        # Folder permissions must permit the application user to read the files.
        stage.chmod(0o755)
        for path in stage.rglob("*"):
            if path.is_dir():
                path.chmod(0o755)
        restore(bundle / "base.db", destination / "base.db")
        if (destination / "uploads").exists():
            (destination / "uploads").rename(destination / (".uploads-before-restore-" + uuid.uuid4().hex))
        stage.rename(destination / "uploads")
        actual = upload_inventory(destination / "uploads")
        if database_metadata(destination / "base.db") != manifest["database"] or set(actual) != set(manifest["uploads"]) or any(
                actual[name][key] != manifest["uploads"][name][key]
                for name in actual for key in ("sha256", "bytes")):
            raise RuntimeError("Restored data verification failed; keep writers stopped")
        return manifest
    finally:
        if stage.exists():
            shutil.rmtree(stage)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("snapshot", "verify", "restore"))
    parser.add_argument("source")
    parser.add_argument("destination", nargs="?")
    args = parser.parse_args()
    if args.action != "verify" and not args.destination:
        parser.error("destination required")
    result = (verify_bundle(args.source) if args.action == "verify" else
              {"snapshot": snapshot_bundle, "restore": restore_bundle}[args.action](args.source, args.destination))
    print(json.dumps({"verified": True, "uploads": len(result["uploads"]),
                      "foreign_key_violations": result["database"]["foreign_key_violations"]}))
