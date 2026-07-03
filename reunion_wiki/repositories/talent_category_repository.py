# -*- coding: utf-8 -*-

from ..db import get_db_connection


def _fetchone(query, params=()):
    """Exécute une requête SELECT et retourne une seule catégorie talent.

    Args:
        query (str): Requête SQL paramétrée.
        params (tuple): Paramètres de la requête.

    Returns:
        sqlite3.Row | None:
            Ligne trouvée ou None.
    """

    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute(query, params)
        return cur.fetchone()
    finally:
        conn.close()


def _fetchall(query, params=()):
    """Exécute une requête SELECT et retourne des catégories talents.

    Args:
        query (str): Requête SQL paramétrée.
        params (tuple): Paramètres de la requête.

    Returns:
        list[sqlite3.Row]:
            Lignes retournées par SQLite.
    """

    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute(query, params)
        return cur.fetchall()
    finally:
        conn.close()


def _execute(query, params=()):
    """Exécute une requête d'écriture sur les catégories talents.

    Args:
        query (str): Requête SQL paramétrée.
        params (tuple): Paramètres de la requête.

    Returns:
        int:
            Nombre de lignes modifiées ou supprimées.
    """

    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute(query, params)
        conn.commit()
        return cur.rowcount
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def _insert(query, params=()):
    """Exécute un INSERT sur les catégories talents.

    Args:
        query (str): Requête SQL paramétrée.
        params (tuple): Paramètres de la requête.

    Returns:
        int:
            Identifiant de la catégorie créée.
    """

    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute(query, params)
        conn.commit()
        return cur.lastrowid
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def get_by_id(category_id):
    """Récupère une catégorie talent à partir de son identifiant.

    Args:
        category_id (int): Identifiant de la catégorie talent.

    Returns:
        sqlite3.Row | None:
            Catégorie trouvée ou None.
    """

    return _fetchone(
        """
        SELECT id, name, slug
        FROM talent_categories
        WHERE id = ?
        """,
        (category_id,),
    )


def get_by_name(name):
    """Récupère une catégorie talent à partir de son nom.

    Args:
        name (str): Nom de catégorie talent.

    Returns:
        sqlite3.Row | None:
            Catégorie trouvée ou None.
    """

    return _fetchone(
        """
        SELECT id, name, slug
        FROM talent_categories
        WHERE name = ?
        """,
        (name,),
    )


def get_by_name_excluding_id(name, category_id):
    """Récupère une catégorie talent par nom en ignorant un identifiant.

    Args:
        name (str): Nom de catégorie talent.
        category_id (int): Identifiant de catégorie à exclure.

    Returns:
        sqlite3.Row | None:
            Catégorie trouvée ou None.
    """

    return _fetchone(
        """
        SELECT id, name, slug
        FROM talent_categories
        WHERE name = ?
          AND id != ?
        """,
        (name, category_id),
    )


def get_by_slug(slug):
    """Récupère une catégorie talent à partir de son slug.

    Args:
        slug (str): Slug de catégorie talent.

    Returns:
        sqlite3.Row | None:
            Catégorie trouvée ou None.
    """

    return _fetchone(
        """
        SELECT id, name, slug
        FROM talent_categories
        WHERE slug = ?
        """,
        (slug,),
    )


def get_by_slug_excluding_id(slug, category_id):
    """Récupère une catégorie talent par slug en ignorant un identifiant.

    Args:
        slug (str): Slug de catégorie talent.
        category_id (int): Identifiant de catégorie à exclure.

    Returns:
        sqlite3.Row | None:
            Catégorie trouvée ou None.
    """

    return _fetchone(
        """
        SELECT id, name, slug
        FROM talent_categories
        WHERE slug = ?
          AND id != ?
        """,
        (slug, category_id),
    )


def list_all():
    """Liste toutes les catégories talents.

    Returns:
        list[sqlite3.Row]:
            Catégories talents triées par nom.
    """

    return _fetchall(
        """
        SELECT id, name, slug
        FROM talent_categories
        ORDER BY name COLLATE NOCASE ASC
        """
    )


def insert(name, slug):
    """Insère une catégorie talent.

    Args:
        name (str): Nom de la catégorie talent.
        slug (str): Slug unique de la catégorie talent.

    Returns:
        int:
            Identifiant de la catégorie créée.
    """

    return _insert(
        """
        INSERT INTO talent_categories (name, slug)
        VALUES (?, ?)
        """,
        (name, slug),
    )


def update(category_id, name, slug):
    """Met à jour une catégorie talent.

    Args:
        category_id (int): Identifiant de la catégorie talent.
        name (str): Nouveau nom.
        slug (str): Nouveau slug.

    Returns:
        int:
            Nombre de lignes mises à jour.
    """

    return _execute(
        """
        UPDATE talent_categories
        SET name = ?, slug = ?
        WHERE id = ?
        """,
        (name, slug, category_id),
    )


def delete(category_id):
    """Supprime une catégorie talent.

    Args:
        category_id (int): Identifiant de la catégorie talent.

    Returns:
        int:
            Nombre de lignes supprimées.
    """

    return _execute("DELETE FROM talent_categories WHERE id = ?", (category_id,))


def count_talents_by_category(category_id):
    """Compte les talents associés à une catégorie talent.

    Args:
        category_id (int): Identifiant de la catégorie talent.

    Returns:
        sqlite3.Row:
            Ligne contenant le total de talents associés.
    """

    return _fetchone(
        """
        SELECT COUNT(*) AS total
        FROM talents
        WHERE category_id = ?
        """,
        (category_id,),
    )
