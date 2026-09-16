# -*- coding: utf-8 -*-
"""Service d'envoi des notifications par e-mail."""

import smtplib
import ssl
from email.message import EmailMessage

from flask import current_app, render_template


def send_submission_notification(payload):
    """Envoie un e-mail lorsqu'un site est proposé."""
    if not current_app.config.get("MAIL_ENABLED"):
        return

    server = current_app.config.get("MAIL_SERVER")
    recipients = current_app.config.get("MAIL_RECIPIENTS", [])
    if not server or not recipients:
        current_app.logger.warning(
            "Notification e-mail non envoyée : serveur ou destinataires non configurés."
        )
        return

    sender = (
        current_app.config.get("MAIL_DEFAULT_SENDER")
        or current_app.config.get("MAIL_USERNAME")
        or recipients[0]
    )
    message = EmailMessage()
    message["Subject"] = f"Nouvelle proposition Réunion Wiki : {payload.get('nom')}"
    message["From"] = sender
    message["To"] = ", ".join(recipients)
    message.set_content(render_template("emails/new_submission.txt", **payload))

    context = ssl.create_default_context()
    try:
        if current_app.config.get("MAIL_USE_SSL"):
            with smtplib.SMTP_SSL(
                server,
                current_app.config.get("MAIL_PORT"),
                context=context,
            ) as smtp:
                username = current_app.config.get("MAIL_USERNAME")
                password = current_app.config.get("MAIL_PASSWORD")
                if username and password:
                    smtp.login(username, password)
                smtp.send_message(message)
        else:
            with smtplib.SMTP(server, current_app.config.get("MAIL_PORT")) as smtp:
                smtp.ehlo()
                if current_app.config.get("MAIL_USE_TLS"):
                    smtp.starttls(context=context)
                username = current_app.config.get("MAIL_USERNAME")
                password = current_app.config.get("MAIL_PASSWORD")
                if username and password:
                    smtp.login(username, password)
                smtp.send_message(message)
    except Exception as error:
        current_app.logger.error(
            f"Erreur lors de l'envoi de l'e-mail de notification: {error}"
        )
