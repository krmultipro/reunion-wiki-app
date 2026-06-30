# -*- coding: utf-8 -*-
"""Formulaires d'administration des talents."""

from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileSize
from wtforms import HiddenField, IntegerField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional, URL

from . import _normalize_url, _sanitize_basic, _sanitize_multiline, _strip_filter
from ..services.talent_service import STATUSES


class TalentForm(FlaskForm):
    """Création et édition d'un talent depuis l'administration."""

    name = StringField(
        "Nom",
        [
            DataRequired(message="Le nom est obligatoire."),
            Length(min=2, max=160, message="Le nom doit faire entre 2 et 160 caractères."),
        ],
        filters=[_sanitize_basic],
    )
    slug = StringField(
        "Slug (optionnel, généré automatiquement si vide)",
        [Optional(), Length(max=180, message="Slug trop long.")],
        filters=[_sanitize_basic],
    )
    category = StringField(
        "Catégorie",
        [
            DataRequired(message="La catégorie est obligatoire."),
            Length(max=120, message="Catégorie trop longue."),
        ],
        filters=[_sanitize_basic],
    )
    city = StringField(
        "Commune",
        [Optional(), Length(max=120, message="Commune trop longue.")],
        filters=[_sanitize_basic],
    )
    description = TextAreaField(
        "Description courte",
        [
            DataRequired(message="La description est obligatoire."),
            Length(max=500, message="La description ne doit pas dépasser 500 caractères."),
        ],
        filters=[_sanitize_multiline],
    )
    bio = TextAreaField(
        "Biographie",
        [Optional()],
        filters=[_sanitize_multiline],
    )
    image = FileField(
        "Image",
        validators=[
            Optional(),
            FileAllowed(["jpg", "jpeg", "png", "webp", "gif"], "Image JPG, PNG, WEBP ou GIF uniquement."),
            FileSize(max_size=3 * 1024 * 1024, message="Image trop lourde (3 Mo maximum)."),
        ],
    )
    instagram_url = StringField(
        "Instagram",
        [Optional(), URL(message="URL Instagram invalide.")],
        filters=[_normalize_url],
    )
    youtube_url = StringField(
        "YouTube",
        [Optional(), URL(message="URL YouTube invalide.")],
        filters=[_normalize_url],
    )
    tiktok_url = StringField(
        "TikTok",
        [Optional(), URL(message="URL TikTok invalide.")],
        filters=[_normalize_url],
    )
    facebook_url = StringField(
        "Facebook",
        [Optional(), URL(message="URL Facebook invalide.")],
        filters=[_normalize_url],
    )
    website_url = StringField(
        "Site officiel",
        [Optional(), URL(message="URL du site invalide.")],
        filters=[_normalize_url],
    )
    status = SelectField(
        "Statut",
        choices=STATUSES,
        default="draft",
        validators=[DataRequired()],
        filters=[_strip_filter],
    )
    display_order = IntegerField(
        "Ordre d'affichage",
        [Optional()],
        default=0,
    )
    submit = SubmitField("Enregistrer")


class TalentActionForm(FlaskForm):
    """Formulaire CSRF pour les actions admin sur un talent."""

    talent_id = HiddenField(validators=[DataRequired()])
