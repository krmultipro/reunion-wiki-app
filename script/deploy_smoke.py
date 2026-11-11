"""Anonymous, read-only HTTP checks; also executable via stdin in an older image."""

import argparse
from contextlib import closing
import os
from pathlib import Path
import sqlite3
import time
from urllib.parse import quote, urljoin
from urllib.request import urlopen


def find_public_upload(database_path, uploads_path):
    """Choose an existing image referenced by a published record, using SQLite RO."""
    database = Path(database_path)
    uploads = Path(uploads_path).resolve()
    if not database.is_file() or not uploads.is_dir():
        return None
    with closing(sqlite3.connect(database.resolve().as_uri() + "?mode=ro", uri=True)) as db:
        for table, field in (("talents", "image"), ("content", "featured_image")):
            columns = {row[1] for row in db.execute("PRAGMA table_info(" + table + ")")}
            if not {field, "status"}.issubset(columns):
                continue
            for (raw,) in db.execute(
                    "SELECT " + field + " FROM " + table +
                    " WHERE status = ? AND " + field + " IS NOT NULL ORDER BY " + field,
                    ("published",)):
                if not isinstance(raw, str) or not raw.startswith("uploads/"):
                    continue
                relative = Path(raw[len("uploads/"):])
                if relative.is_absolute() or ".." in relative.parts or "uploads/" + relative.as_posix() != raw:
                    continue
                image = uploads / relative
                if (image.resolve().is_relative_to(uploads) and not image.is_symlink()
                        and image.is_file() and image.suffix.lower() in
                        {".jpg", ".jpeg", ".png", ".webp", ".gif", ".svg", ".ico"}):
                    return "/static/uploads/" + quote(relative.as_posix())
    return None


def check_pages(base_url, upload=None):
    """Check rendered public/login pages and an image without following tracking links."""
    for path in ("/", "/recherche?q=reunion", "/admin/login"):
        with urlopen(urljoin(base_url, path), timeout=3) as response:
            body = response.read()
            if response.status != 200 or response.headers.get_content_type() != "text/html" or not body:
                raise RuntimeError("Invalid HTML response: " + path)
            if path == "/admin/login" and b'type="password"' not in body:
                raise RuntimeError("Login form missing")
    for path in ["/static/favicon.ico"] + ([upload] if upload else []):
        with urlopen(urljoin(base_url, path), timeout=3) as response:
            if response.status != 200 or not response.headers.get_content_type().startswith("image/") or not response.read():
                raise RuntimeError("Invalid image response: " + path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("base_url", nargs="?", default="http://127.0.0.1:8000/")
    parser.add_argument("--upload")
    parser.add_argument("--attempts", type=int, default=20)
    args = parser.parse_args()
    if not args.upload:
        args.upload = find_public_upload(
            os.getenv("DATABASE_PATH", "/data/base.db"),
            os.getenv("UPLOAD_FOLDER", "/data/uploads"))
        if not args.upload:
            print("Aucune image publiée disponible : contrôle limité au favicon.")
    if args.attempts < 1:
        parser.error("--attempts must be positive")
    for attempt in range(args.attempts):
        try:
            check_pages(args.base_url, args.upload)
            print("Smoke HTTP OK: accueil, recherche, connexion admin anonyme, images.")
            break
        except Exception:
            if attempt == args.attempts - 1:
                raise
            time.sleep(2)
