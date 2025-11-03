# -*- coding: utf-8 -*-
"""
Formulaires avec validation pour Réunion Wiki
SÉCURITÉ : Validation côté serveur pour éviter les injections
"""

from flask_wtf import FlaskForm
from wtforms import HiddenField, IntegerField, PasswordField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, URL, ValidationError, Optional
import re


def _strip_filter(value):
    return value.strip() if isinstance(value, str) else value


def _sanitize_basic(value):
    if not isinstance(value, str):
        return value
    value = value.strip()
    # Supprime les balises HTML et les caractères de contrôle invisibles
    value = re.sub(r"<[^>]+>", "", value)
    value = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F]", "", value)
    return value


def _sanitize_multiline(value):
    if not isinstance(value, str):
        return value
    value = value.strip()
    value = re.sub(r"<[^>]+>", "", value)
    value = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F]", "", value)
    value = value.replace("\r\n", "\n").replace("\r", "\n")
    value = re.sub(r"\n{3,}", "\n\n", value)
    return value


class SiteForm(FlaskForm):
    """Formulaire de proposition de site avec validation complète"""
    
    nom = StringField('Nom du site', [
        DataRequired(message="Le nom du site est obligatoire"),
        Length(min=2, max=100, message="Le nom doit faire entre 2 et 100 caractères")
    ], filters=[_sanitize_basic])
    
    ville = StringField('Ville', [
        Length(max=50, message="Le nom de la ville ne peut pas dépasser 50 caractères")
    ], filters=[_sanitize_basic])
    
    lien = StringField('Lien du site', [
        DataRequired(message="Le lien du site est obligatoire"),
        URL(message="Veuillez entrer une URL valide (ex: https://example.com)")
    ], filters=[_sanitize_basic])
    
    description = TextAreaField('Description', [
        DataRequired(message="La description est obligatoire"),
        Length(min=10, max=500, message="La description doit faire entre 10 et 500 caractères")
    ], filters=[_sanitize_multiline])
    
    categorie = SelectField('Catégorie', [
        DataRequired(message="Veuillez sélectionner une catégorie")
    ], choices=[], filters=[_strip_filter])
    honeypot = StringField('Ne pas remplir ce champ', render_kw={"autocomplete": "off"}, filters=[_strip_filter])
    
    def validate_nom(self, field):
        """Validation personnalisée pour le nom"""
        # Évite les caractères dangereux
        if re.search(r'[<>"\']', field.data or ""):
            raise ValidationError("Le nom ne peut pas contenir les caractères < > \" '")
    
    def validate_description(self, field):
        """Validation personnalisée pour la description"""
        # Évite les scripts et balises HTML
        if re.search(r'<script|javascript:|on\w+\s*=', field.data, re.IGNORECASE):
            raise ValidationError("La description contient du contenu non autorisé")
    
    def validate_lien(self, field):
        """Validation personnalisée pour le lien"""
        # S'assure que l'URL commence par http ou https
        if not field.data.startswith(('http://', 'https://')):
            raise ValidationError("L'URL doit commencer par http:// ou https://")

    def validate_honeypot(self, field):
        """Champ trappé pour les robots : doit rester vide"""
        if field.data:
            raise ValidationError("Formulaire invalide.")


class AdminLoginForm(FlaskForm):
    """Formulaire de connexion à l'espace de modération"""

    username = StringField(
        "Identifiant",
        [
            DataRequired(message="Identifiant requis"),
            Length(max=80, message="Identifiant trop long"),
        ],
        filters=[_sanitize_basic],
    )
    password = PasswordField(
        "Mot de passe",
        [DataRequired(message="Mot de passe requis")],
    )
    submit = SubmitField("Se connecter")


class ModerationActionForm(FlaskForm):
    """Actions de modération sur une proposition"""

    site_id = HiddenField(validators=[DataRequired()])


class TalentProposalForm(FlaskForm):
    """Formulaire public pour proposer un talent Instagram"""

    pseudo = StringField(
        "Pseudo Instagram",
        [
            DataRequired(message="Le pseudo est obligatoire"),
            Length(min=2, max=80, message="Le pseudo doit faire entre 2 et 80 caractères"),
        ],
        filters=[_sanitize_basic],
    )

    instagram = StringField(
        "Lien Instagram",
        [
            DataRequired(message="Le lien Instagram est obligatoire"),
            URL(message="Veuillez saisir une URL valide (ex : https://www.instagram.com/...)"),
            Length(max=255, message="Le lien est trop long"),
        ],
        filters=[_sanitize_basic],
    )

    description = TextAreaField(
        "Description du talent",
        [
            DataRequired(message="Décris le talent en quelques mots"),
            Length(min=10, max=300, message="La description doit faire entre 10 et 300 caractères"),
        ],
        filters=[_sanitize_multiline],
    )

    honeypot = StringField("Ne pas remplir ce champ", render_kw={"autocomplete": "off"}, filters=[_strip_filter])

    def validate_instagram(self, field):
        """Vérifie que l'URL pointe bien vers un profil Instagram"""
        if not field.data.startswith(("http://", "https://")):
            raise ValidationError("L'URL doit commencer par http:// ou https://")
        if "instagram.com" not in field.data.lower():
            raise ValidationError("Le lien doit provenir d'Instagram.")

    def validate_honeypot(self, field):
        if field.data:
            raise ValidationError("Formulaire invalide.")


class TalentAdminForm(FlaskForm):
    """Formulaire d'administration pour gérer les talents"""

    pseudo = StringField(
        "Pseudo Instagram",
        [
            DataRequired(message="Le pseudo est obligatoire"),
            Length(min=2, max=80, message="Le pseudo doit faire entre 2 et 80 caractères"),
        ],
        filters=[_sanitize_basic],
    )

    instagram = StringField(
        "Lien Instagram",
        [
            DataRequired(message="Le lien Instagram est obligatoire"),
            URL(message="Veuillez saisir une URL valide"),
            Length(max=255, message="Le lien est trop long"),
        ],
        filters=[_sanitize_basic],
    )

    description = TextAreaField(
        "Description",
        [
            DataRequired(message="La description est obligatoire"),
            Length(min=10, max=400, message="La description doit faire entre 10 et 400 caractères"),
        ],
        filters=[_sanitize_multiline],
    )

    category = SelectField(
        "Catégorie",
        [Optional()],
        choices=[],
        filters=[_strip_filter],
    )

    image = StringField(
        "Image (optionnelle)",
        [
            Optional(),
            Length(max=255, message="Le chemin de l'image est trop long"),
        ],
        filters=[_sanitize_basic],
    )

    status = SelectField(
        "Statut",
        [
            DataRequired(message="Le statut est obligatoire"),
        ],
        choices=[
            ("en_attente", "En attente"),
            ("valide", "Publié"),
            ("refuse", "Refusé"),
        ],
        filters=[_strip_filter],
    )

    display_order = IntegerField(
        "Ordre d'affichage",
        [
            Optional(),
        ],
        default=0,
        render_kw={"type": "number", "min": "0", "step": "1"},
    )

    def validate_instagram(self, field):
        if not field.data.startswith(("http://", "https://")):
            raise ValidationError("L'URL doit commencer par http:// ou https://")
        if "instagram.com" not in field.data.lower():
            raise ValidationError("Le lien doit provenir d'Instagram.")


class TalentModerationActionForm(FlaskForm):
    """Actions de modération sur un talent"""

    talent_id = HiddenField(validators=[DataRequired()])
