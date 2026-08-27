# -*- coding: utf-8 -*-
"""
Formulaires avec validation pour Réunion Wiki
SÉCURITÉ : Validation côté serveur pour éviter les injections
"""

import re

from flask_wtf import FlaskForm
from wtforms import BooleanField, HiddenField, PasswordField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, URL, ValidationError

from .filters import _normalize_url, _sanitize_basic, _sanitize_multiline, _strip_filter


class SiteForm(FlaskForm):
    """Formulaire de proposition de site avec validation complète"""
    
    nom = StringField('Nom du site', [
        DataRequired(message="Le nom du site est obligatoire"),
        Length(min=2, max=100, message="Le nom doit faire entre 2 et 100 caractères")
    ], filters=[_sanitize_basic])
    
    ville = SelectField('Ville', choices=[], filters=[_strip_filter])
    
    lien = StringField('Lien du site', [
        DataRequired(message="Le lien du site est obligatoire"),
        URL(message="Veuillez entrer une URL valide (ex: example.com ou https://example.com)")
    ], filters=[_normalize_url])

    
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
        if not field.data.startswith(("http://", "https://")):
            raise ValidationError("URL invalide")


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


class AdminLogoutForm(FlaskForm):
    """Formulaire de déconnexion admin (POST + CSRF)."""

    submit = SubmitField("Déconnexion")


class ModerationActionForm(FlaskForm):
    """Actions de modération sur une proposition"""

    site_id = HiddenField(validators=[DataRequired()])
    return_to = HiddenField()


class AdminSiteForm(SiteForm):
    """Formulaire complet pour la création/édition d'un site côté admin"""

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


class CategoryForm(FlaskForm):
    """CRUD catégories côté admin"""

    nom = StringField(
        "Nom de la catégorie",
        validators=[
            DataRequired(message="Le nom de la catégorie est obligatoire"),
            Length(min=2, max=80, message="La catégorie doit faire entre 2 et 80 caractères"),
        ],
        filters=[_sanitize_basic],
    )
    submit = SubmitField("Enregistrer")


class DeleteCategoryForm(FlaskForm):
    """Suppression d'une catégorie"""

    category_id = HiddenField(validators=[DataRequired()])


class DeleteClickForm(FlaskForm):
    """Suppression d'un événement de clic."""

    click_id = HiddenField(validators=[DataRequired()])
