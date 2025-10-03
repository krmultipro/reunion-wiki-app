# -*- coding: utf-8 -*-
"""
Formulaires avec validation pour Réunion Wiki
SÉCURITÉ : Validation côté serveur pour éviter les injections
"""

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, validators
from wtforms.validators import DataRequired, Length, URL, ValidationError
import re

class SiteForm(FlaskForm):
    """Formulaire de proposition de site avec validation complète"""
    
    nom = StringField('Nom du site', [
        DataRequired(message="Le nom du site est obligatoire"),
        Length(min=2, max=100, message="Le nom doit faire entre 2 et 100 caractères")
    ])
    
    ville = StringField('Ville', [
        Length(max=50, message="Le nom de la ville ne peut pas dépasser 50 caractères")
    ])
    
    lien = StringField('Lien du site', [
        DataRequired(message="Le lien du site est obligatoire"),
        URL(message="Veuillez entrer une URL valide (ex: https://example.com)")
    ])
    
    description = TextAreaField('Description', [
        DataRequired(message="La description est obligatoire"),
        Length(min=10, max=500, message="La description doit faire entre 10 et 500 caractères")
    ])
    
    categorie = SelectField('Catégorie', [
        DataRequired(message="Veuillez sélectionner une catégorie")
    ], choices=[])
    
    def validate_nom(self, field):
        """Validation personnalisée pour le nom"""
        # Évite les caractères dangereux
        if re.search(r'[<>"\']', field.data):
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
