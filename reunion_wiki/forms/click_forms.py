# -*- coding: utf-8 -*-
"""Formulaires d'administration des événements de clic."""

from flask_wtf import FlaskForm
from wtforms import HiddenField
from wtforms.validators import DataRequired


class DeleteClickForm(FlaskForm):
    """Suppression d'un événement de clic (POST + CSRF)."""

    click_id = HiddenField(validators=[DataRequired()])
