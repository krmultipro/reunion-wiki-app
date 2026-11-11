# -*- coding: utf-8 -*-
"""Formulaires publics et administratifs des sites référencés."""

import re

from flask_wtf import FlaskForm
from wtforms import BooleanField, HiddenField, SelectField, StringField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional, URL, ValidationError

from .filters import _normalize_url, _sanitize_basic, _sanitize_multiline, _strip_filter
from ..repositories.site_refusal_repository import REASON_CHOICES


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
    portee = SelectField(
        "Portée géographique",
        choices=[
            ("", "Non précisée"),
            ("island", "Toute La Réunion"),
            ("online", "En ligne"),
        ],
        default="",
        filters=[_strip_filter],
    )

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

    def validate_portee(self, field):
        if field.data and self.ville.data:
            raise ValidationError("Choisissez une commune ou une portée, pas les deux.")

    def validate_honeypot(self, field):
        """Rejette les robots qui remplissent le champ invisible."""
        if field.data:
            raise ValidationError("Formulaire invalide.")


class ModerationActionForm(FlaskForm):
    """Action de modération sur une proposition de site (POST + CSRF)."""

    site_id = HiddenField(validators=[DataRequired()])
    return_to = HiddenField()
    refusal_reason = SelectField("Motif de refus", choices=REASON_CHOICES, validators=[Optional()])


class ManualHttpReviewForm(FlaskForm):
    """Confirmation humaine après une réponse HTTP 401 ou 403."""

    site_id = HiddenField(validators=[DataRequired()])
    check_id = HiddenField(validators=[DataRequired()])
    note = TextAreaField(
        "Note de vérification",
        validators=[
            DataRequired(message="La note de vérification est obligatoire."),
            Length(
                min=10,
                max=500,
                message="La note doit faire entre 10 et 500 caractères.",
            ),
        ],
        filters=[_sanitize_multiline],
    )


class EditorialReviewForm(FlaskForm):
    """Explicit human decision on the site's connection with La Réunion."""

    reviewed_url = HiddenField(validators=[DataRequired()])
    criterion = SelectField(
        "Lien avec La Réunion",
        choices=[
            ("", "Choisir une décision"),
            ("local_organization", "Entreprise, association ou organisme réunionnais"),
            ("reunion_content", "Contenu consacré à La Réunion"),
            ("national_local_offer", "Service national avec page ou offre locale"),
            ("useful_resource", "Ressource particulièrement utile au public réunionnais"),
            ("no_link", "Aucun lien réel constaté — refuser la publication"),
        ],
        validators=[DataRequired(message="Choisissez une décision éditoriale.")],
    )
    note = TextAreaField("Justification facultative", validators=[Length(max=500)], filters=[_sanitize_multiline])
    evidence_url = StringField(
        "URL de preuve facultative",
        validators=[Optional(), URL(message="Entrez une URL HTTP ou HTTPS valide.")],
        filters=[_strip_filter],
    )

    def validate_evidence_url(self, field):
        if field.data and not field.data.startswith(("http://", "https://")):
            raise ValidationError("Entrez une URL HTTP ou HTTPS valide.")


class AdminSiteForm(SiteForm):
    """Création et modification d'un site depuis l'administration."""

    status = SelectField(
        "Statut",
        choices=[
            ("draft", "Brouillon"),
            ("valide", "Publié"),
            ("en_attente", "En attente"),
            ("refuse", "Refusé"),
            ("archived", "Archivé"),
        ],
        default="valide",
    )
    en_vedette = BooleanField("Mettre en vedette", default=False)
    new_publication = BooleanField("Traiter comme une nouvelle publication", default=False)
    refusal_reason = SelectField("Motif de refus", choices=REASON_CHOICES, validators=[Optional()])
