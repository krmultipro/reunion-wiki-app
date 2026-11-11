# -*- coding: utf-8 -*-
"""Formulaires d'administration des événements de clic."""

from flask_wtf import FlaskForm
from wtforms import HiddenField, IntegerField, StringField
from wtforms.validators import AnyOf, DataRequired, InputRequired, Length, NumberRange, Regexp


class CorrectAggregateForm(FlaskForm):
    """Correction auditée d'un compteur géographique agrégé."""

    site_id = HiddenField(validators=[DataRequired(), Regexp(r"^[1-9][0-9]*$")])
    stat_date = HiddenField(validators=[DataRequired(), Regexp(r"^\d{4}-\d{2}-\d{2}$")])
    zone = HiddenField(validators=[AnyOf(("Nord", "Sud", "Est", "Ouest", "Hors Réunion", "Inconnu"))])
    new_count = IntegerField(validators=[InputRequired(), NumberRange(min=0)])
    reason = StringField(validators=[DataRequired(), Length(min=3, max=300)])
