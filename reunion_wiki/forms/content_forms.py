# -*- coding: utf-8 -*-
"""Formulaires de la plateforme de contenu SEO.

La validation « champs requis à la publication » (meta title/description) est
appliquée dans le service, pas ici : un brouillon peut rester incomplet.
"""

from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileSize
from wtforms import HiddenField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional

from . import _sanitize_basic, _sanitize_multiline
from ..services.content_service import CONTENT_TYPES, STATUSES


def _strip_filter(value):
    """Nettoie les espaces sans toucher au HTML (assaini ensuite par le service)."""
    return value.strip() if isinstance(value, str) else value


class ContentForm(FlaskForm):
    """Création et édition d'un contenu SEO (champs V1 uniquement)."""

    content_type = SelectField(
        "Type de contenu",
        choices=CONTENT_TYPES,
        validators=[DataRequired(message="Le type de contenu est obligatoire")],
        filters=[_strip_filter],
    )
    title = StringField(
        "Titre",
        [
            DataRequired(message="Le titre est obligatoire"),
            Length(min=2, max=200, message="Le titre doit faire entre 2 et 200 caractères"),
        ],
        filters=[_sanitize_basic],
    )
    slug = StringField(
        "Slug (optionnel, généré automatiquement si vide)",
        [Optional(), Length(max=200, message="Slug trop long")],
        filters=[_sanitize_basic],
    )
    summary = TextAreaField(
        "Résumé",
        [Optional(), Length(max=500, message="Le résumé ne doit pas dépasser 500 caractères")],
        filters=[_sanitize_multiline],
    )
    body = TextAreaField(
        "Contenu",
        [Optional()],
        filters=[_strip_filter],  # HTML assaini par content_service.sanitize_html
    )
    featured_image = FileField(
        "Image à la une",
        validators=[
            Optional(),
            FileAllowed(["jpg", "jpeg", "png", "webp", "gif"], "Image JPG, PNG, WEBP ou GIF uniquement."),
            FileSize(max_size=3 * 1024 * 1024, message="Image trop lourde (3 Mo maximum)."),
        ],
    )
    meta_title = StringField(
        "Meta title",
        [Optional(), Length(max=120, message="Meta title trop long")],
        filters=[_sanitize_basic],
    )
    meta_description = TextAreaField(
        "Meta description",
        [Optional(), Length(max=320, message="Meta description trop longue")],
        filters=[_sanitize_basic],
    )
    status = SelectField(
        "Statut",
        choices=STATUSES,
        default="draft",
        validators=[DataRequired()],
        filters=[_strip_filter],
    )
    submit = SubmitField("Enregistrer")


class ContentDeleteForm(FlaskForm):
    """Suppression d'un contenu (POST + CSRF)."""

    content_id = HiddenField(validators=[DataRequired()])
