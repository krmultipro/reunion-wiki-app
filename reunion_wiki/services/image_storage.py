# -*- coding: utf-8 -*-

import os
import secrets
from datetime import datetime

from flask import current_app
from werkzeug.utils import secure_filename


# Upload volontairement minimal pour la V1 : pas de retaille ni de miniature.
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp", "gif"}
ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
MAX_IMAGE_BYTES = 3 * 1024 * 1024  # 3 Mo


class ImageStorageError(Exception):
    """Erreur métier levée quand un upload d'image est refusé."""


def _extension(filename: str) -> str:
    """Retourne l'extension en minuscules d'un nom de fichier.

    Args:
        filename (str): Nom de fichier d'origine.

    Returns:
        str: Extension sans point, ou chaîne vide.
    """

    if "." not in filename:
        return ""
    return filename.rsplit(".", 1)[-1].lower()


def save_upload(file_storage, namespace=None):
    """Valide et enregistre une image uploadée sur le disque.

    L'image est écrite sous le dossier configuré `UPLOAD_FOLDER`, avec un nom
    sécurisé et un préfixe aléatoire pour éviter les collisions. Seul le chemin
    relatif au dossier statique est retourné : il a vocation à être stocké en
    base, jamais le binaire.

    Args:
        file_storage: Objet `FileStorage` issu d'un FileField WTForms.
        namespace (str | None): Sous-dossier métier optionnel, par exemple
            `talents` ou `content`.

    Returns:
        str: Chemin relatif au dossier statique
            (ex: 'uploads/talents/2026/06/ab12-x.jpg').

    Raises:
        ImageStorageError: Si l'extension, le type MIME ou la taille sont invalides.
    """

    filename = (file_storage.filename or "").strip()
    if not filename:
        raise ImageStorageError("Aucun fichier image fourni.")

    extension = _extension(filename)
    if extension not in ALLOWED_EXTENSIONS:
        raise ImageStorageError(
            "Format d'image non autorisé. Utilisez JPG, PNG, WEBP ou GIF."
        )

    if file_storage.mimetype not in ALLOWED_MIME_TYPES:
        raise ImageStorageError("Type de fichier non autorisé.")

    # Mesure la taille sans charger le fichier en mémoire.
    stream = file_storage.stream
    stream.seek(0, os.SEEK_END)
    size = stream.tell()
    stream.seek(0)
    if size == 0:
        raise ImageStorageError("Le fichier image est vide.")
    if size > MAX_IMAGE_BYTES:
        raise ImageStorageError("Image trop lourde (3 Mo maximum).")

    now = datetime.utcnow()
    parts = [now.strftime("%Y"), now.strftime("%m")]
    if namespace:
        parts.insert(0, secure_filename(namespace))

    relative_dir = os.path.join(*parts)
    upload_root = current_app.config["UPLOAD_FOLDER"]
    absolute_dir = os.path.join(upload_root, relative_dir)
    os.makedirs(absolute_dir, exist_ok=True)

    safe_name = secure_filename(filename) or f"image.{extension}"
    unique_name = f"{secrets.token_hex(8)}-{safe_name}"
    absolute_path = os.path.join(absolute_dir, unique_name)
    file_storage.save(absolute_path)

    # Toujours en séparateurs URL pour un usage direct dans les templates.
    return os.path.join("uploads", relative_dir, unique_name).replace(os.sep, "/")


def delete_upload(relative_path):
    """Supprime un fichier uploadé en restant dans le dossier configuré.

    Args:
        relative_path (str | None): Chemin public stocké en base, généralement
            préfixé par ``uploads/``.

    Returns:
        bool:
            True si un fichier a été supprimé, False s'il était absent ou si
            le chemin fourni ne désignait pas un upload autorisé.
    """

    if not relative_path:
        return False

    normalized_path = str(relative_path).replace("\\", "/").lstrip("/")
    if not normalized_path.startswith("uploads/"):
        return False

    upload_root = os.path.abspath(current_app.config["UPLOAD_FOLDER"])
    relative_upload_path = normalized_path.removeprefix("uploads/")
    absolute_path = os.path.abspath(os.path.join(upload_root, relative_upload_path))

    try:
        if os.path.commonpath([upload_root, absolute_path]) != upload_root:
            return False
    except ValueError:
        return False

    try:
        os.remove(absolute_path)
    except FileNotFoundError:
        return False
    except OSError:
        current_app.logger.warning("Impossible de supprimer l'image uploadée %s", normalized_path)
        return False
    return True
