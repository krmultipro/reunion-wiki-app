"""Email helpers (submission notifications, etc.)."""

from __future__ import annotations

import smtplib
import ssl
from email.message import EmailMessage
from typing import Any, Mapping

from flask import current_app, render_template


def send_submission_notification(payload: Mapping[str, Any]) -> None:
    """Send an email when a new site is proposed, if mail is configured."""
    app = current_app
    if not app.config.get("MAIL_ENABLED"):
        return

    server = app.config.get("MAIL_SERVER")
    recipients = app.config.get("MAIL_RECIPIENTS", [])
    if not server or not recipients:
        app.logger.warning(
            "Notification email non envoyée : serveur ou destinataires non configurés."
        )
        return

    sender = (
        app.config.get("MAIL_DEFAULT_SENDER")
        or app.config.get("MAIL_USERNAME")
        or recipients[0]
    )

    message = EmailMessage()
    message["Subject"] = f"Nouvelle proposition Réunion Wiki : {payload.get('nom')}"
    message["From"] = sender
    message["To"] = ", ".join(recipients)
    message.set_content(render_template("emails/new_submission.txt", **payload))

    context = ssl.create_default_context()
    try:
        if app.config.get("MAIL_USE_SSL"):
            with smtplib.SMTP_SSL(
                server, app.config.get("MAIL_PORT"), context=context
            ) as smtp:
                _smtp_login_if_needed(smtp)
                smtp.send_message(message)
        else:
            with smtplib.SMTP(server, app.config.get("MAIL_PORT")) as smtp:
                smtp.ehlo()
                if app.config.get("MAIL_USE_TLS"):
                    smtp.starttls(context=context)
                _smtp_login_if_needed(smtp)
                smtp.send_message(message)
    except smtplib.SMTPException as exc:
        app.logger.error(f"Erreur lors de l'envoi de l'email de notification: {exc}")


def _smtp_login_if_needed(smtp: smtplib.SMTP) -> None:
    """Login to the SMTP server if credentials are configured."""
    app = current_app
    username = app.config.get("MAIL_USERNAME")
    password = app.config.get("MAIL_PASSWORD")
    if username and password:
        smtp.login(username, password)
