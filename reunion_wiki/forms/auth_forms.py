# -*- coding: utf-8 -*-
"""Formulaires d'authentification de l'administration."""

from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Length

from .filters import _sanitize_basic


class AdminLoginForm(FlaskForm):
    """Formulaire de connexion à l'espace de modération."""

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
