# -*- coding: utf-8 -*-

from dataclasses import dataclass

from flask import current_app, session

from ..repositories import click_repository, site_repository
from ..utils import get_client_ip
from .click_privacy_service import build_visitor_token, resolve_zone, reunion_day


KNOWN_BOT_PATTERNS = [
    "websiphon",
    "googleother",
    "gptbot",
    "claudebot",
    "bytespider",
    "semrushbot",
    "ahrefsbot",
    "mj12bot",
    "dotbot",
    "petalbot",
    "amazonbot",
    "crawler",
    "spider",
]


@dataclass(frozen=True)
class ClickResult:
    """
    Représente le résultat métier d'une tentative de clic sortant.

    Args:
        url (str | None): URL de destination quand le site existe.
        found (bool): indique si le site ciblé a été trouvé.
    """

    url: str | None
    found: bool


def is_known_bot(user_agent: str) -> bool:
    """
    Détecte si un User-Agent contient un motif de robot connu.

    Args:
        user_agent (str): valeur de l'en-tête HTTP User-Agent.

    Returns:
        bool: True si le clic doit être ignoré pour les statistiques.
    """

    ua_lower = (user_agent or "").lower()
    return any(pattern in ua_lower for pattern in KNOWN_BOT_PATTERNS)


def is_bot(user_agent: str) -> bool:
    """
    Indique si un User-Agent doit être traité comme un robot.

    Args:
        user_agent (str): valeur de l'en-tête HTTP User-Agent.

    Returns:
        bool: True si le clic doit être ignoré pour les statistiques.
    """

    return is_known_bot(user_agent)


def handle_click(site_id: int, headers) -> ClickResult:
    """
    Orchestre la gestion métier d'un clic sortant.

    Args:
        site_id (int): identifiant du site demandé par la route /go/<site_id>.
        headers: en-têtes HTTP de la requête Flask.

    Returns:
        ClickResult: destination à rediriger et état d'existence du site.

    Règles métier:
        - un site inexistant ou non valide ne produit aucun clic;
        - les robots ne sont pas comptabilisés;
        - une même empreinte ne doit pas être recomptée si un clic récent existe déjà.
    """

    current_app.logger.info(f"[GO] Tentative de redirection pour site_id={site_id}")

    row = site_repository.get_valid_site_by_id(site_id)
    if not row:
        current_app.logger.warning(f"[GO] Site introuvable ou non valide id={site_id}")
        return ClickResult(url=None, found=False)

    current_app.logger.info(
        f"[GO] Site trouvé id={site_id} | ancien compteur={row['click_count']} | url={row['lien']}"
    )

    if session.get("admin_authenticated"):
        current_app.logger.info(f"[GO] Administrateur détecté, clic ignoré id={site_id}")
        return ClickResult(url=row["lien"], found=True)

    ip = get_client_ip()
    user_agent = (headers.get("User-Agent", "") or "")[:400]

    # Ignore les robots afin de ne pas fausser les statistiques.
    if is_known_bot(user_agent):
        current_app.logger.info(f"[GO] Bot détecté, clic ignoré id={site_id} ua={user_agent}")
        return ClickResult(url=row["lien"], found=True)

    visitor_token = build_visitor_token(ip, user_agent, site_id)
    zone = resolve_zone(ip)
    if click_repository.register_aggregated_click(site_id, visitor_token, zone, reunion_day()):
        current_app.logger.info(f"[GO] Clic validé id={site_id} zone={zone}")
    else:
        current_app.logger.info(f"[GO] Clic ignoré (trop récent) id={site_id}")

    return ClickResult(url=row["lien"], found=True)
