# -*- coding: utf-8 -*-

from dataclasses import dataclass

from flask import current_app

from ..repositories import click_repository, site_repository
from ..utils import get_client_ip


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


def is_bot(user_agent: str) -> bool:
    """
    Détecte si un User-Agent correspond probablement à un robot.

    Args:
        user_agent (str): valeur de l'en-tête HTTP User-Agent.

    Returns:
        bool: True si le clic doit être ignoré pour les statistiques.
    """

    ua_lower = (user_agent or "").lower()
    return "bot" in ua_lower or "crawl" in ua_lower or "spider" in ua_lower


def should_count_click(site_id: int, ip_address: str):
    """
    Indique si un clic doit être comptabilisé pour un site et une IP.

    Args:
        site_id (int): identifiant du site visité.
        ip_address (str): adresse IP du visiteur.

    Returns:
        bool: True si aucun clic récent n'existe pour ce couple site/IP.
    """

    # Évite de compter plusieurs clics récents de la même IP pour le même site.
    return not click_repository.get_click_by_ip_and_site(site_id, ip_address)


def register_click(site_id: int, ip_address: str, user_agent: str):
    """
    Enregistre un clic valide et incrémente le compteur du site.

    Args:
        site_id (int): identifiant du site cliqué.
        ip_address (str): adresse IP du visiteur.
        user_agent (str): User-Agent tronqué du visiteur.

    Returns:
        Any: valeur retournée par le repository de clics.
    """

    return click_repository.insert_click_and_increment_count(site_id, ip_address, user_agent)


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
        - une même IP ne doit pas être recomptée si un clic récent existe déjà.
    """

    current_app.logger.info(f"[GO] Tentative de redirection pour site_id={site_id}")

    row = site_repository.get_valid_site_by_id(site_id)
    if not row:
        current_app.logger.warning(f"[GO] Site introuvable ou non valide id={site_id}")
        return ClickResult(url=None, found=False)

    current_app.logger.info(
        f"[GO] Site trouvé id={site_id} | ancien compteur={row['click_count']} | url={row['lien']}"
    )

    ip = get_client_ip()
    user_agent = (headers.get("User-Agent", "") or "")[:400]

    # Ignore les robots afin de ne pas fausser les statistiques.
    if is_bot(user_agent):
        current_app.logger.info(f"[GO] Bot détecté, clic ignoré id={site_id} ua={user_agent}")
        return ClickResult(url=row["lien"], found=True)

    if should_count_click(site_id, ip):
        register_click(site_id, ip, user_agent)
        current_app.logger.info(f"[GO] Clic validé id={site_id} ip={ip}")
    else:
        current_app.logger.info(f"[GO] Clic ignoré (trop récent) id={site_id} ip={ip}")

    return ClickResult(url=row["lien"], found=True)
