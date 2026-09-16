# -*- coding: utf-8 -*-
"""Formulaires publics et administratifs des sites référencés."""

import re

from flask_wtf import FlaskForm
from wtforms import BooleanField, HiddenField, SelectField, StringField, TextAreaField
from wtforms.validators import DataRequired, Length, URL, ValidationError

from .filters import _normalize_url, _sanitize_basic, _sanitize_multiline, _strip_filter


class SiteForm(FlaskForm):
    """Formulaire public de proposition d'un site."""

    nom = StringField(
        "Nom du site",
        [
            DataRequired(message="Le nom du site est obligatoire"),
            Length(min=2, max=100, message="Le nom doit faire entre 2 et 100 caractères"),
        ],
        filters=[_sanitize_basic],
    )

    ville = SelectField("Ville", choices=[], filters=[_strip_filter])

    lien = StringField(
        "Lien du site",
        [
            DataRequired(message="Le lien du site est obligatoire"),
            URL(message="Veuillez entrer une URL valide (ex: example.com ou https://example.com)"),
        ],
        filters=[_normalize_url],
    )

    description = TextAreaField(
        "Description",
        [
            DataRequired(message="La description est obligatoire"),
            Length(min=10, max=500, message="La description doit faire entre 10 et 500 caractères"),
        ],
        filters=[_sanitize_multiline],
    )

    categorie = SelectField(
        "Catégorie",
        [DataRequired(message="Veuillez sélectionner une catégorie")],
        choices=[],
        filters=[_strip_filter],
    )
    honeypot = StringField(
        "Ne pas remplir ce champ",
        render_kw={"autocomplete": "off"},
        filters=[_strip_filter],
    )

    def validate_nom(self, field):
        """Refuse les caractères dangereux dans le nom."""
        if re.search(r'[<>"\']', field.data or ""):
            raise ValidationError("Le nom ne peut pas contenir les caractères < > \" '")

    def validate_description(self, field):
        """Refuse les motifs courants de scripts et de gestionnaires HTML."""
        if re.search(r'<script|javascript:|on\w+\s*=', field.data, re.IGNORECASE):
            raise ValidationError("La description contient du contenu non autorisé")

    def validate_lien(self, field):
        """Vérifie que l'URL normalisée utilise HTTP ou HTTPS."""
        if not field.data.startswith(("http://", "https://")):
            raise ValidationError("URL invalide")

    def validate_honeypot(self, field):
        """Rejette les robots qui remplissent le champ invisible."""
        if field.data:
            raise ValidationError("Formulaire invalide.")


class ModerationActionForm(FlaskForm):
    """Action de modération sur une proposition de site (POST + CSRF)."""

    site_id = HiddenField(validators=[DataRequired()])
    return_to = HiddenField()


class AdminSiteForm(SiteForm):
    """Création et modification d'un site depuis l'administration."""

    status = SelectField(
        "Statut",
        choices=[
            ("valide", "Publié"),
            ("en_attente", "En attente"),
            ("refuse", "Refusé"),
        ],
        default="valide",
    )
    en_vedette = BooleanField("Mettre en vedette", default=False)
