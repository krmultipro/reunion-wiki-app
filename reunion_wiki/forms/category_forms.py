# -*- coding: utf-8 -*-
"""Formulaires d'administration des catégories de sites."""

from flask_wtf import FlaskForm
from wtforms import HiddenField, StringField, SubmitField
from wtforms.validators import DataRequired, Length

from .filters import _sanitize_basic


class CategoryForm(FlaskForm):
    """Création et modification d'une catégorie depuis l'administration."""

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
    """Suppression d'une catégorie (POST + CSRF)."""

    category_id = HiddenField(validators=[DataRequired()])
