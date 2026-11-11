"""Évite de renouveler une session pendant le chargement d'un fichier public."""

from flask import request
from flask.sessions import SecureCookieSessionInterface


def is_public_static_response(response, session):
    """Identifie un fichier public réussi qui ne dépend pas de la session."""
    return (request.endpoint == 'static'
            and response.status_code in (200, 304)
            and not session.modified
            and not session.accessed)


class StaticAssetSessionInterface(SecureCookieSessionInterface):
    """Conserve la session Flask et son renouvellement sur les documents privés."""

    def save_session(self, app, session, response):
        """Ne renouvelle aucun cookie sur un fichier commun indépendant de la session."""
        # Flask sauvegarde la session après les hooks after_request : agir ici
        # évite Set-Cookie et Vary: Cookie sans toucher aux autres valeurs Vary.
        if is_public_static_response(response, session):
            return
        super().save_session(app, session, response)
