"""Reject private files and unsafe members in the application-only DEV archive."""

import argparse
from pathlib import PurePosixPath
import tarfile


ALLOWED_ROOTS = {
    "app.py", "migrate.py", "requirements.txt", "Dockerfile", ".dockerignore",
    "reunion_wiki", "templates", "static", "script", "tests",
}
PRIVATE_PARTS = {
    "maquettes", "monitoring", "apercu-prive", "data", "data_dev", "data_prod",
    "uploads", "uploads_dev", "uploads_prod", "backups", "certbot", "logs",
    "reports", ".refonte-runtime", ".git", ".venv", "__pycache__",
}


def validate_archive(path):
    """Refuse non-application roots, private paths, traversal and symbolic links."""
    with tarfile.open(path) as archive:
        members = archive.getmembers()
        if not members:
            raise ValueError("Archive vide")
        for member in members:
            name = PurePosixPath(member.name)
            parts = name.parts
            if not parts:  # tar may contain the root directory itself.
                continue
            if name.is_absolute() or ".." in parts or parts[0] not in ALLOWED_ROOTS:
                raise ValueError("Archive hors périmètre applicatif")
            lowered = [part.lower() for part in parts]
            if any(part in PRIVATE_PARTS or part.startswith(".env") or
                   part == "sephora.jpeg" or any(suffix in PurePosixPath(part).suffixes for suffix in (".db", ".sqlite", ".sqlite3")) or
                   part.endswith((".db-wal", ".db-shm", ".pyc")) for part in lowered):
                raise ValueError("Fichier privé ou runtime interdit dans l’archive")
            if not (member.isfile() or member.isdir()):
                raise ValueError("Lien ou fichier spécial interdit dans l’archive")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive")
    validate_archive(parser.parse_args().archive)
