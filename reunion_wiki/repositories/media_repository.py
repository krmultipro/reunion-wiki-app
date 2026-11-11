"""Lectures de visibilité des médias persistants, sans données justificatives."""

from ..db import get_db_connection


def is_published_media(relative_path):
    """Indique si un fichier est référencé par un contenu actuellement publié.

    Args:
        relative_path (str): Chemin public relatif, préfixé par uploads/.

    Returns:
        bool: True uniquement si une fiche publiée référence ce fichier.
    """
    connection = get_db_connection()
    try:
        tables = {row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        for table, field in (("talents", "image"), ("content", "featured_image")):
            if table not in tables:
                continue
            row = connection.execute(
                f"SELECT 1 FROM {table} WHERE {field} = ? AND status = 'published' LIMIT 1",
                (relative_path,),
            ).fetchone()
            if row:
                return True
        return False
    finally:
        connection.close()
