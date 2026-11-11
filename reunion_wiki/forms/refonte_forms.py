"""Server forms for the simple anonymous proposal and moderation journey."""
from urllib.parse import urlsplit
from flask_wtf import FlaskForm
from wtforms import HiddenField, SelectField, StringField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional, Regexp, ValidationError
from .filters import _strip_filter
from ..repositories.site_refusal_repository import REASON_CHOICES


class ProposalForm(FlaskForm):
    """Collect only the public proposal's necessary and optional private values."""
    kind = SelectField('Que souhaites-tu proposer ?', choices=[('site','Un site'),('personality','Une personnalité')], validators=[DataRequired()])
    nonce = HiddenField(validators=[DataRequired(),Length(max=100)])
    name = StringField('Nom', validators=[DataRequired(message='Indique un nom.'),Length(min=2,max=100)], filters=[_strip_filter])
    url = StringField('Lien officiel', validators=[DataRequired(message='Indique un lien HTTP ou HTTPS.'),Length(max=255)], filters=[_strip_filter])
    description = TextAreaField('Présentation', validators=[Length(max=500)], filters=[_strip_filter])
    category_id = SelectField('Catégorie', choices=[], coerce=int, default=0)
    email = StringField('Ton email (facultatif, privé)', validators=[Optional(),Regexp(r'^[^\s@<>]+@[^\s@<>]+\.[^\s@<>]+$',message='Indique un email valide.'),Length(max=254)], filters=[_strip_filter])
    reunion_attachment = TextAreaField('Lien avec La Réunion (facultatif, privé)', validators=[Optional(),Length(max=1000)], filters=[_strip_filter])
    location = SelectField('Commune ou portée (facultatif)', choices=[('', 'Non précisée')], default='')
    supplied_evidence_url = StringField('Lien de preuve proposé (facultatif, privé)', validators=[Optional(),Length(max=255)], filters=[_strip_filter])
    honeypot = StringField('Laisse ce champ vide', filters=[_strip_filter])

    def validate_honeypot(self, field):
        """Reject the hidden field's automated submissions."""
        if field.data:
            raise ValidationError('Formulaire invalide.')

    def validate_url(self, field):
        """Reject executable and malformed URL schemes before persistence."""
        value = field.data or ''
        if '://' not in value:
            value = 'https://' + value
        try:
            parts = urlsplit(value)
            valid = parts.scheme in ('http','https') and parts.hostname and not parts.username and not parts.password and not any(c.isspace() for c in value)
            parts.port
        except ValueError:
            valid = False
        if not valid:
            raise ValidationError('Indique une URL HTTP ou HTTPS valide.')
        field.data = value

    def validate_category_id(self, field):
        """Require the site's category but allow minimal personality proposals."""
        if self.kind.data == 'site' and not field.data:
            raise ValidationError('Choisis une catégorie.')

    def validate_description(self, field):
        """Keep the existing minimum site description requirement."""
        if self.kind.data == 'site' and len(field.data or '') < 10:
            raise ValidationError('Décris le site en au moins 10 caractères.')


class ProposalAdminForm(ProposalForm):
    """Edit the minimal editorial record and choose an explicit admin action."""
    kind = HiddenField(validators=[DataRequired()])
    nonce = HiddenField(validators=[Optional()])
    action = SelectField('Action', choices=[('save','Enregistrer'),('prepare','Préparer le brouillon'),('publish','Publier après vérification'),('reject','Refuser'),('archive','Archiver')])
    private_source_reference = StringField('Référence privée de la source', validators=[Optional(),Length(max=500)], filters=[_strip_filter])
    private_source_url = StringField('URL privée de la source', validators=[Optional(),Length(max=255)], filters=[_strip_filter])
    private_source_note = TextAreaField('Note privée de vérification', validators=[Optional(),Length(max=1000)], filters=[_strip_filter])
    refusal_reason = SelectField('Motif privé du refus', choices=REASON_CHOICES, validators=[Optional()])
    editorial_criterion = SelectField('Lien du site avec La Réunion', choices=[('', 'Choisir une décision'),('local_organization','Organisme réunionnais'),('reunion_content','Contenu consacré à La Réunion'),('national_local_offer','Offre locale'),('useful_resource','Ressource utile au public réunionnais')], validators=[Optional()])
    confirm = SelectField('Confirmation de l’action', choices=[('','Choisir'),('yes','Je confirme la publication ou l’archivage')], validators=[Optional()])
