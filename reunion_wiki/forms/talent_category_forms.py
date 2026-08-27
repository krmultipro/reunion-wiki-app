# -*- coding: utf-8 -*-
"""Formulaires d'administration des catégories de créateurs."""

from flask_wtf import FlaskForm
from wtforms import HiddenField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, Optional

from .filters import _sanitize_basic


class TalentCategoryForm(FlaskForm):
    """Création et édition d'une catégorie de créateurs."""

    name = StringField(
        "Nom de la catégorie",
        validators=[
            DataRequired(message="Le nom de la catégorie est obligatoire."),
            Length(min=2, max=120, message="La catégorie doit faire entre 2 et 120 caractères."),
        ],
        filters=[_sanitize_basic],
    )
    slug = StringField(
        "Slug (optionnel, généré automatiquement si vide)",
        validators=[
            Optional(),
            Length(max=160, message="Le slug ne doit pas dépasser 160 caractères."),
        ],
        filters=[_sanitize_basic],
    )
    submit = SubmitField("Enregistrer")


class TalentCategoryActionForm(FlaskForm):
    """Formulaire CSRF pour les actions sur une catégorie de créateurs."""

    category_id = HiddenField(validators=[DataRequired()])
