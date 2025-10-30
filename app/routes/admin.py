"""Administration routes (dashboard, moderation, talents)."""

from __future__ import annotations

import sqlite3

from flask import (
    Blueprint,
    abort,
    flash,
    current_app,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from ..database import get_db_connection
from ..extensions import limiter
from ..forms import (
    AdminLoginForm,
    ModerationActionForm,
    SiteForm,
    TalentAdminForm,
    TalentModerationActionForm,
)
from ..services.auth import admin_required, verify_admin_credentials
from ..services.sites import get_categories
from ..services.talents import (
    TALENT_STATUSES,
    TALENT_STATUS_LABELS,
    get_talent_category_choices,
    get_talent_status_choices,
    prepare_talents_storage,
)

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/login", methods=["GET", "POST"])
@limiter.limit("5 per minute")
def login():
    form = AdminLoginForm()
    next_url = request.args.get("next")
    if not next_url or not next_url.startswith("/"):
        next_url = url_for("admin.dashboard")

    if form.validate_on_submit():
        if verify_admin_credentials(form.username.data, form.password.data):
            session.permanent = True
            session["admin_authenticated"] = True
            session["admin_username"] = form.username.data
            current_app.logger.info(
                "Connexion admin réussie pour '%s' depuis %s",
                form.username.data,
                request.remote_addr or "IP inconnue",
            )
            flash("Connexion réussie.", "success")
            return redirect(next_url)
        current_app.logger.warning(
            "Échec connexion admin pour '%s' depuis %s",
            form.username.data,
            request.remote_addr or "IP inconnue",
        )
        flash("Identifiants invalides.", "error")

    return render_template("admin/login.html", form=form, next_url=next_url)


@admin_bp.route("/logout")
def logout():
    username = session.get("admin_username") or "inconnu"
    current_app.logger.info(
        "Déconnexion admin pour '%s' depuis %s",
        username,
        request.remote_addr or "IP inconnue",
    )
    session.pop("admin_authenticated", None)
    session.pop("admin_username", None)
    flash("Déconnexion effectuée.", "success")
    return redirect(url_for("admin.login"))


@admin_bp.route("/", methods=["GET"])
@admin_bp.route("", methods=["GET"])
@admin_required
def dashboard():
    status_filter = request.args.get("status", "en_attente")
    search_query = request.args.get("q", "").strip()
    allowed_statuses = {"en_attente", "valide", "refuse", "tout"}
    if status_filter not in allowed_statuses:
        status_filter = "en_attente"

    conn = get_db_connection()
    if not conn:
        flash("Impossible de se connecter à la base de données.", "error")
        return redirect(url_for("public.accueil"))

    try:
        cur = conn.cursor()
        params: list[str] = []
        query_clause = ""

        if search_query and len(search_query) >= 2:
            like_query = f"%{search_query}%"
            query_clause = """AND (
                    nom LIKE ? COLLATE NOCASE
                    OR categorie LIKE ? COLLATE NOCASE
                    OR description LIKE ? COLLATE NOCASE
                    OR IFNULL(ville, '') LIKE ? COLLATE NOCASE
                    OR lien LIKE ? COLLATE NOCASE
                )"""
            params.extend([like_query] * 5)

        status_clause = ""
        if status_filter != "tout":
            status_clause = "AND status = ?"
            params.append(status_filter)

        cur.execute(
            f"""
            SELECT id, nom, categorie, ville, lien, description, status, date_ajout
            FROM sites
            WHERE 1 = 1
            {status_clause}
            {query_clause}
            ORDER BY
                CASE WHEN status = 'en_attente' THEN 0 ELSE 1 END,
                date_ajout DESC,
                id DESC
            LIMIT 200
            """,
            tuple(params),
        )
        entries = cur.fetchall()

        cur.execute("SELECT status, COUNT(*) as total FROM sites GROUP BY status")
        stats_rows = cur.fetchall()
    except sqlite3.Error as exc:
        current_app.logger.error(
            f"Erreur lors de la récupération des propositions: {exc}"
        )
        flash("Erreur lors de la récupération des propositions.", "error")
        entries = []
        stats_rows = []
    finally:
        conn.close()

    stats = {row["status"]: row["total"] for row in stats_rows}
    stats["tout"] = sum(stats.values())

    action_forms = {}
    for site in entries:
        form = ModerationActionForm()
        form.site_id.data = str(site["id"])
        action_forms[site["id"]] = form

    return render_template(
        "admin/dashboard.html",
        entries=entries,
        stats=stats,
        status_filter=status_filter,
        search_query=search_query,
        action_forms=action_forms,
        admin_username=session.get("admin_username"),
    )


@admin_bp.route("/propositions/<int:site_id>", methods=["POST"])
@admin_required
def update_site(site_id: int):
    form = ModerationActionForm()
    if not form.validate_on_submit():
        flash("Formulaire invalide.", "error")
        return redirect(url_for("admin.dashboard"))

    try:
        site_id_form = int(form.site_id.data)
    except (TypeError, ValueError):
        abort(400)

    if site_id_form != site_id:
        abort(400)

    action = request.form.get("action")
    if action not in {"approve", "reject", "delete"}:
        flash("Action inconnue.", "error")
        return redirect(url_for("admin.dashboard"))

    status_redirect = request.form.get("status_filter", "en_attente")
    query_redirect = request.form.get("search_query", "")

    conn = get_db_connection()
    if not conn:
        flash("Impossible d'accéder à la base de données.", "error")
        return redirect(
            url_for(
                "admin.dashboard",
                status=status_redirect,
                q=query_redirect,
            )
        )

    try:
        cur = conn.cursor()
        if action == "approve":
            cur.execute(
                "UPDATE sites SET status = 'valide', date_ajout = DATETIME('now') WHERE id = ?",
                (site_id,),
            )
            message = "Proposition validée et publiée."
        elif action == "reject":
            cur.execute(
                "UPDATE sites SET status = 'refuse' WHERE id = ?",
                (site_id,),
            )
            message = "Proposition refusée."
        else:
            cur.execute("DELETE FROM sites WHERE id = ?", (site_id,))
            message = "Proposition supprimée."

        if cur.rowcount == 0:
            flash("La proposition est introuvable.", "error")
            conn.rollback()
        else:
            conn.commit()
            current_app.logger.info(
                "Action admin '%s' sur proposition #%s par '%s' (%s)",
                action,
                site_id,
                session.get("admin_username") or "inconnu",
                request.remote_addr or "IP inconnue",
            )
            flash(message, "success")
    except sqlite3.Error as exc:
        conn.rollback()
        current_app.logger.error(
            f"Erreur lors de la mise à jour du site {site_id}: {exc}"
        )
        flash("Erreur lors de la mise à jour.", "error")
    finally:
        conn.close()

    return redirect(
        url_for("admin.dashboard", status=status_redirect, q=query_redirect)
    )


@admin_bp.route("/propositions/<int:site_id>/edit", methods=["GET", "POST"])
@admin_required
def edit_site(site_id: int):
    form = SiteForm()
    form.honeypot.data = ""
    categories_list = get_categories()
    form.categorie.choices = [(cat, cat) for cat in categories_list]
    form.categorie.choices.insert(0, ("", "Sélectionnez une catégorie"))

    conn = get_db_connection()
    if not conn:
        flash("Impossible de se connecter à la base de données.", "error")
        return redirect(url_for("admin.dashboard"))

    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT id, nom, ville, lien, description, categorie, status
            FROM sites
            WHERE id = ?
            """,
            (site_id,),
        )
        site = cur.fetchone()
    except sqlite3.Error as exc:
        current_app.logger.error(
            f"Erreur lors de la récupération de la proposition {site_id}: {exc}"
        )
        flash("Erreur lors de la récupération.", "error")
        conn.close()
        return redirect(url_for("admin.dashboard"))

    if not site:
        conn.close()
        flash("Proposition introuvable.", "error")
        return redirect(url_for("admin.dashboard"))

    if request.method == "GET":
        form.nom.data = site["nom"]
        form.ville.data = site["ville"] or ""
        form.lien.data = site["lien"]
        form.description.data = site["description"]
        form.categorie.data = site["categorie"] or ""

    if form.validate_on_submit():
        conn_to_update = get_db_connection()
        if not conn_to_update:
            flash("Impossible de se connecter à la base de données.", "error")
            conn.close()
            return redirect(url_for("admin.dashboard"))
        try:
            cur_update = conn_to_update.cursor()
            cur_update.execute(
                """
                UPDATE sites
                SET nom = ?, ville = ?, lien = ?, description = ?, categorie = ?, status = ?
                WHERE id = ?
                """,
                (
                    form.nom.data,
                    form.ville.data or None,
                    form.lien.data,
                    form.description.data,
                    form.categorie.data,
                    request.form.get("status") or site["status"],
                    site_id,
                ),
            )
            if cur_update.rowcount == 0:
                flash("La mise à jour a échoué : proposition introuvable.", "error")
                conn_to_update.rollback()
            else:
                conn_to_update.commit()
                flash("Proposition mise à jour avec succès.", "success")
                current_app.logger.info(
                    "Mise à jour admin de la proposition #%s par '%s' (%s)",
                    site_id,
                    session.get("admin_username") or "inconnu",
                    request.remote_addr or "IP inconnue",
                )
                conn.close()
                conn_to_update.close()
                return redirect(url_for("admin.dashboard"))
            conn_to_update.close()
        except sqlite3.Error as exc:
            conn_to_update.rollback()
            conn_to_update.close()
            conn.close()
            current_app.logger.error(
                f"Erreur lors de la mise à jour du site {site_id}: {exc}"
            )
            flash("Erreur lors de la mise à jour.", "error")
            return redirect(url_for("admin.dashboard"))

    conn.close()
    return render_template(
        "admin/edit_site.html",
        form=form,
        site=site,
        admin_username=session.get("admin_username"),
        form_action=url_for(
            "admin.edit_site",
            site_id=site_id,
            status=request.args.get("status"),
            q=request.args.get("q"),
        ),
        submit_label="Enregistrer les modifications",
        page_title=f"Modifier la proposition #{site_id}",
        subtitle=f"Statut actuel : <strong>{site['status']}</strong>",
        status_filter=request.args.get("status", "en_attente"),
        search_query=request.args.get("q", ""),
    )


@admin_bp.route("/propositions/new", methods=["GET", "POST"])
@admin_required
def create_site():
    form = SiteForm()
    form.honeypot.data = ""
    categories_list = get_categories()
    form.categorie.choices = [(cat, cat) for cat in categories_list]
    form.categorie.choices.insert(0, ("", "Sélectionnez une catégorie"))

    posted_category = request.form.get("categorie")
    if posted_category and posted_category not in [choice[0] for choice in form.categorie.choices]:
        form.categorie.choices.append((posted_category, posted_category))

    if form.validate_on_submit():
        conn = get_db_connection()
        if not conn:
            flash("Impossible de se connecter à la base de données.", "error")
            return redirect(url_for("admin.dashboard", status="valide"))
        try:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO sites (nom, ville, lien, description, categorie, status, date_ajout, en_vedette)
                VALUES (?, ?, ?, ?, ?, 'valide', DATETIME('now'), 0)
                """,
                (
                    form.nom.data,
                    form.ville.data or None,
                    form.lien.data,
                    form.description.data,
                    form.categorie.data,
                ),
            )
            conn.commit()
            flash("Nouveau site ajouté et publié.", "success")
            current_app.logger.info(
                "Création admin d'un site (%s) par '%s' (%s)",
                form.lien.data,
                session.get("admin_username") or "inconnu",
                request.remote_addr or "IP inconnue",
            )
            return redirect(url_for("admin.dashboard"))
        except sqlite3.Error as exc:
            conn.rollback()
            current_app.logger.error(
                f"Erreur lors de la création d'un site depuis l'admin: {exc}"
            )
            flash("Erreur lors de l'ajout du site.", "error")
        finally:
            conn.close()

    return render_template(
        "admin/edit_site.html",
        form=form,
        site=None,
        admin_username=session.get("admin_username"),
        form_action=url_for("admin.create_site"),
        submit_label="Publier le site",
        page_title="Ajouter un nouveau site",
        subtitle="Complète les champs pour publier le site instantanément.",
        status_filter="valide",
        search_query="",
    )


@admin_bp.route("/talents", methods=["GET"])
@admin_required
def talents():
    prepare_talents_storage()
    status_filter = request.args.get("status", "en_attente")
    allowed_statuses = set(TALENT_STATUSES + ["tout"])
    if status_filter not in allowed_statuses:
        status_filter = "en_attente"

    search_query = request.args.get("q", "").strip()

    conn = get_db_connection()
    if not conn:
        flash("Impossible de se connecter à la base de données.", "error")
        return redirect(url_for("admin.dashboard"))

    try:
        cur = conn.cursor()
        params: list[str] = []
        query = """
            SELECT id, pseudo, instagram, description, category, image, status, date_created, date_updated
            FROM talents
            WHERE 1 = 1
        """

        if status_filter != "tout":
            query += " AND status = ?"
            params.append(status_filter)

        if search_query and len(search_query) >= 2:
            like_query = f"%{search_query}%"
            query += """
                AND (
                    pseudo LIKE ? COLLATE NOCASE
                    OR instagram LIKE ? COLLATE NOCASE
                    OR description LIKE ? COLLATE NOCASE
                    OR IFNULL(category, '') LIKE ? COLLATE NOCASE
                )
            """
            params.extend([like_query] * 4)

        query += """
            ORDER BY
                CASE status
                    WHEN 'en_attente' THEN 0
                    WHEN 'valide' THEN 1
                    ELSE 2
                END,
                date_updated DESC,
                id DESC
            LIMIT 200
        """

        cur.execute(query, tuple(params))
        entries = cur.fetchall()

        cur.execute("SELECT status, COUNT(*) AS total FROM talents GROUP BY status")
        stats_rows = cur.fetchall()
    except sqlite3.Error as exc:
        current_app.logger.error(
            f"Erreur lors de la récupération des talents admin: {exc}"
        )
        flash("Erreur lors de la récupération des talents.", "error")
        entries = []
        stats_rows = []
    finally:
        conn.close()

    stats = {row["status"]: row["total"] for row in stats_rows}
    stats["tout"] = sum(stats.values())

    action_forms = {}
    for talent in entries:
        form = TalentModerationActionForm()
        form.talent_id.data = str(talent["id"])
        action_forms[talent["id"]] = form

    return render_template(
        "admin/talents.html",
        entries=entries,
        stats=stats,
        status_filter=status_filter,
        search_query=search_query,
        action_forms=action_forms,
        admin_username=session.get("admin_username"),
        status_labels=TALENT_STATUS_LABELS,
    )


@admin_bp.route("/talents/<int:talent_id>", methods=["POST"])
@admin_required
def update_talent(talent_id: int):
    prepare_talents_storage()
    form = TalentModerationActionForm()
    if not form.validate_on_submit():
        flash("Formulaire invalide.", "error")
        return redirect(url_for("admin.talents"))

    try:
        talent_id_form = int(form.talent_id.data)
    except (TypeError, ValueError):
        abort(400)

    if talent_id_form != talent_id:
        abort(400)

    action = request.form.get("action")
    if action not in {"approve", "reject", "delete"}:
        flash("Action inconnue.", "error")
        return redirect(url_for("admin.talents"))

    status_redirect = request.form.get("status_filter", "en_attente")
    query_redirect = request.form.get("search_query", "").strip()
    allowed_statuses = set(TALENT_STATUSES + ["tout"])
    if status_redirect not in allowed_statuses:
        status_redirect = "en_attente"

    conn = get_db_connection()
    if not conn:
        flash("Impossible d'accéder à la base de données.", "error")
        return redirect(
            url_for(
                "admin.talents",
                status=status_redirect,
                q=query_redirect,
            )
        )

    try:
        cur = conn.cursor()
        if action == "approve":
            cur.execute(
                "UPDATE talents SET status = 'valide', date_updated = DATETIME('now') WHERE id = ?",
                (talent_id,),
            )
            message = "Talent publié."
        elif action == "reject":
            cur.execute(
                "UPDATE talents SET status = 'refuse', date_updated = DATETIME('now') WHERE id = ?",
                (talent_id,),
            )
            message = "Talent refusé."
        else:
            cur.execute("DELETE FROM talents WHERE id = ?", (talent_id,))
            message = "Talent supprimé."

        if cur.rowcount == 0:
            flash("Talent introuvable.", "error")
            conn.rollback()
        else:
            conn.commit()
            current_app.logger.info(
                "Action admin '%s' sur talent #%s par '%s' (%s)",
                action,
                talent_id,
                session.get("admin_username") or "inconnu",
                request.remote_addr or "IP inconnue",
            )
            flash(message, "success")
    except sqlite3.Error as exc:
        conn.rollback()
        current_app.logger.error(
            f"Erreur lors de la mise à jour du talent {talent_id}: {exc}"
        )
        flash("Erreur lors de la mise à jour du talent.", "error")
    finally:
        conn.close()

    return redirect(url_for("admin.talents", status=status_redirect, q=query_redirect))


@admin_bp.route("/talents/<int:talent_id>/edit", methods=["GET", "POST"])
@admin_required
def edit_talent(talent_id: int):
    prepare_talents_storage()
    status_filter = request.args.get("status", "en_attente")
    search_query = request.args.get("q", "").strip()

    form = TalentAdminForm()
    form.category.choices = get_talent_category_choices()
    form.status.choices = get_talent_status_choices()

    conn = get_db_connection()
    if not conn:
        flash("Impossible de se connecter à la base de données.", "error")
        return redirect(url_for("admin.talents", status=status_filter, q=search_query))

    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT id, pseudo, instagram, description, category, image, status
            FROM talents
            WHERE id = ?
            """,
            (talent_id,),
        )
        row = cur.fetchone()
    except sqlite3.Error as exc:
        current_app.logger.error(
            f"Erreur lors de la récupération du talent {talent_id}: {exc}"
        )
        flash("Erreur lors de la récupération du talent.", "error")
        conn.close()
        return redirect(url_for("admin.talents", status=status_filter, q=search_query))

    if not row:
        conn.close()
        flash("Talent introuvable.", "error")
        return redirect(url_for("admin.talents", status=status_filter, q=search_query))

    talent = dict(row)
    conn.close()

    form.category.choices = get_talent_category_choices(talent.get("category"))
    form.status.choices = get_talent_status_choices()

    if request.method == "GET":
        form.pseudo.data = talent["pseudo"]
        form.instagram.data = talent["instagram"]
        form.description.data = talent["description"]
        form.category.data = talent["category"] or ""
        form.image.data = talent["image"] or ""
        form.status.data = talent["status"]

    if form.validate_on_submit():
        conn = get_db_connection()
        if not conn:
            flash("Impossible de se connecter à la base de données.", "error")
            return redirect(
                url_for("admin.talents", status=status_filter, q=search_query)
            )
        try:
            cur = conn.cursor()
            cur.execute(
                """
                UPDATE talents
                SET pseudo = ?, instagram = ?, description = ?, category = ?, image = ?, status = ?, date_updated = DATETIME('now')
                WHERE id = ?
                """,
                (
                    form.pseudo.data,
                    form.instagram.data,
                    form.description.data,
                    form.category.data or "",
                    form.image.data or "",
                    form.status.data,
                    talent_id,
                ),
            )
            if cur.rowcount == 0:
                flash("Aucune mise à jour n'a été effectuée.", "warning")
                conn.rollback()
            else:
                conn.commit()
                flash("Talent mis à jour.", "success")
                current_app.logger.info(
                    "Mise à jour admin du talent #%s par '%s' (%s)",
                    talent_id,
                    session.get("admin_username") or "inconnu",
                    request.remote_addr or "IP inconnue",
                )
                return redirect(
                    url_for("admin.talents", status=status_filter, q=search_query)
                )
        except sqlite3.Error as exc:
            conn.rollback()
            current_app.logger.error(
                f"Erreur lors de la mise à jour du talent {talent_id}: {exc}"
            )
            flash("Erreur lors de la mise à jour du talent.", "error")
        finally:
            conn.close()

    return render_template(
        "admin/edit_talent.html",
        form=form,
        admin_username=session.get("admin_username"),
        form_action=url_for(
            "admin.edit_talent",
            talent_id=talent_id,
            status=status_filter,
            q=search_query,
        ),
        submit_label="Enregistrer les modifications",
        page_title=f"Modifier le talent #{talent_id}",
        subtitle=f"Statut actuel : <strong>{TALENT_STATUS_LABELS.get(talent['status'], talent['status'])}</strong>",
        status_filter=status_filter,
        search_query=search_query,
    )


@admin_bp.route("/talents/new", methods=["GET", "POST"])
@admin_required
def create_talent():
    prepare_talents_storage()
    form = TalentAdminForm()
    form.category.choices = get_talent_category_choices()
    form.status.choices = get_talent_status_choices()

    if form.validate_on_submit():
        conn = get_db_connection()
        if not conn:
            flash("Impossible de se connecter à la base de données.", "error")
            return redirect(url_for("admin.talents"))
        try:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO talents (pseudo, instagram, description, category, image, status)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    form.pseudo.data,
                    form.instagram.data,
                    form.description.data,
                    form.category.data or "",
                    form.image.data or "",
                    form.status.data,
                ),
            )
            conn.commit()
            flash("Talent ajouté.", "success")
            current_app.logger.info(
                "Création admin d'un talent (%s) par '%s' (%s)",
                form.pseudo.data,
                session.get("admin_username") or "inconnu",
                request.remote_addr or "IP inconnue",
            )
            target_status = (
                form.status.data if form.status.data in TALENT_STATUSES else "en_attente"
            )
            return redirect(url_for("admin.talents", status=target_status))
        except sqlite3.Error as exc:
            conn.rollback()
            current_app.logger.error(
                f"Erreur lors de l'ajout d'un talent depuis l'admin: {exc}"
            )
            flash("Erreur lors de l'ajout du talent.", "error")
        finally:
            conn.close()

    return render_template(
        "admin/edit_talent.html",
        form=form,
        admin_username=session.get("admin_username"),
        form_action=url_for("admin.create_talent"),
        submit_label="Enregistrer le talent",
        page_title="Ajouter un talent",
        subtitle="Renseigne les informations du talent Instagram.",
        status_filter="en_attente",
        search_query="",
    )
