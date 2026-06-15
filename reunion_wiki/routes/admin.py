from datetime import datetime
import sqlite3

from flask import Blueprint, abort, current_app, flash, redirect, render_template, request, session, url_for

from ..auth import admin_required, verify_admin_credentials
from ..db import get_db_connection
from ..extensions import limiter
from ..forms import (
    AdminLoginForm,
    AdminLogoutForm,
    AdminSiteForm,
    CategoryForm,
    DeleteCategoryForm,
    DeleteClickForm,
    ModerationActionForm,
)
from ..repositories import category_repository, click_repository, site_repository
from ..taxonomy import (
    generate_unique_category_slug,
    get_categories,
    get_city_choices,
    resolve_category,
    resolve_city,
)
from ..utils import is_safe_next_url, mask_ip, parse_positive_int


admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/admin/login", methods=["GET", "POST"])
@limiter.limit("5 per minute")
def admin_login():
    form = AdminLoginForm()
    next_url = request.args.get("next")
    if not is_safe_next_url(next_url):
        next_url = url_for("admin_dashboard")

    if form.validate_on_submit():
        if verify_admin_credentials(form.username.data, form.password.data):
            session.clear()
            session.permanent = True
            session["admin_authenticated"] = True
            session["admin_username"] = form.username.data
            session["admin_login_at"] = datetime.utcnow().isoformat()
            flash("Connexion réussie.", "success")
            return redirect(next_url)
        flash("Identifiants invalides.", "error")

    return render_template("admin/login.html", form=form, next_url=next_url)


@admin_bp.route("/admin/logout", methods=["POST"])
@admin_required
def admin_logout():
    form = AdminLogoutForm()
    if not form.validate_on_submit():
        abort(400)
    session.clear()
    flash("Déconnexion effectuée.", "success")
    return redirect(url_for("admin_login"))


@admin_bp.route("/admin", methods=["GET"])
@admin_required
def admin_dashboard():
    try:
        pending_sites = site_repository.get_pending_sites()
        stats_rows = site_repository.get_status_counts()
    except sqlite3.Error as e:
        current_app.logger.error(f"Erreur lors de la récupération des propositions: {e}")
        flash("Erreur lors de la récupération des propositions.", "error")
        pending_sites = []
        stats_rows = []

    stats = {row["status"]: row["total"] for row in stats_rows}

    current_path = request.full_path.rstrip("?")
    action_forms = {}
    for site in pending_sites:
        form = ModerationActionForm()
        form.site_id.data = str(site["id"])
        form.return_to.data = current_path
        action_forms[site["id"]] = form

    return render_template(
        "admin/dashboard.html",
        pending_sites=pending_sites,
        stats=stats,
        action_forms=action_forms,
        admin_username=session.get("admin_username"),
    )


@admin_bp.route("/admin/sites", methods=["GET"])
@admin_required
def admin_sites():
    status_filter = (request.args.get("status") or "all").strip()
    city_filter = (request.args.get("city") or "all").strip()
    query_text = (request.args.get("q") or "").strip()
    sort_filter = (request.args.get("sort") or "date_desc").strip()
    page = parse_positive_int(request.args.get("page"), default=1)
    per_page = 50

    allowed_status = {"all", "valide", "en_attente", "refuse"}
    allowed_sorts = {
        "date_desc": "s.date_ajout DESC, s.id DESC",
        "date_asc": "s.date_ajout ASC, s.id ASC",
        "clicks_desc": "s.click_count DESC, s.id DESC",
        "clicks_asc": "s.click_count ASC, s.id ASC",
        "name_asc": "s.nom COLLATE NOCASE ASC, s.id DESC",
        "name_desc": "s.nom COLLATE NOCASE DESC, s.id DESC",
    }

    if status_filter not in allowed_status:
        status_filter = "all"
    if sort_filter not in allowed_sorts:
        sort_filter = "date_desc"
    if len(query_text) > 120:
        query_text = query_text[:120]

    try:
        cities = site_repository.get_admin_city_filters()

        allowed_city_slugs = {row["slug"] for row in cities}
        if city_filter != "all" and city_filter not in allowed_city_slugs:
            city_filter = "all"

        where_clauses = ["1=1"]
        params = []

        if status_filter != "all":
            where_clauses.append("s.status = ?")
            params.append(status_filter)

        if city_filter != "all":
            where_clauses.append("v.slug = ?")
            params.append(city_filter)

        if query_text:
            like = f"%{query_text}%"
            where_clauses.append(
                """
                (
                    s.nom LIKE ?
                    OR COALESCE(c.nom, '') LIKE ?
                    OR s.description LIKE ?
                    OR s.lien LIKE ?
                    OR COALESCE(v.nom, '') LIKE ?
                )
                """
            )
            params.extend([like, like, like, like, like])

        where_sql = " AND ".join(where_clauses)
        sort_sql = allowed_sorts[sort_filter]

        total_sites = site_repository.count_sites_for_admin(where_sql, params)["total"]

        total_pages = max((total_sites + per_page - 1) // per_page, 1)
        if page > total_pages:
            page = total_pages
        offset = (page - 1) * per_page

        all_sites = site_repository.get_sites_for_admin(where_sql, sort_sql, params, per_page, offset)
    except sqlite3.Error as e:
        current_app.logger.error(f"Erreur lors de la récupération des sites: {e}")
        flash("Erreur lors du chargement des sites.", "error")
        all_sites = []
        cities = []
        total_sites = 0
        total_pages = 1
        page = 1

    current_path = request.full_path.rstrip("?")
    action_forms = {}
    for site in all_sites:
        form = ModerationActionForm()
        form.site_id.data = str(site["id"])
        form.return_to.data = current_path
        action_forms[site["id"]] = form

    return render_template(
        "admin/sites.html",
        sites=all_sites,
        action_forms=action_forms,
        cities=cities,
        status_filter=status_filter,
        city_filter=city_filter,
        query_text=query_text,
        sort_filter=sort_filter,
        page=page,
        total_pages=total_pages,
        total_sites=total_sites,
        admin_username=session.get("admin_username"),
    )


@admin_bp.route("/admin/clicks", methods=["GET"])
@admin_required
def admin_clicks():
    query_text = (request.args.get("q") or "").strip()
    sort_filter = (request.args.get("sort") or "newest").strip()
    days_filter = parse_positive_int(request.args.get("days"), default=30)
    page = parse_positive_int(request.args.get("page"), default=1)
    per_page = 100

    if len(query_text) > 120:
        query_text = query_text[:120]
    if sort_filter not in {"newest", "oldest"}:
        sort_filter = "newest"
    if days_filter not in {1, 7, 30, 90, 365}:
        days_filter = 30

    try:
        where_clauses = [
            "sc.clicked_at >= datetime('now', ?)"
        ]
        params = [f"-{days_filter} days"]

        if query_text:
            like = f"%{query_text}%"
            where_clauses.append(
                """
                (
                    s.nom LIKE ?
                    OR COALESCE(c.nom, '') LIKE ?
                    OR COALESCE(v.nom, '') LIKE ?
                    OR s.lien LIKE ?
                    OR sc.user_agent LIKE ?
                )
                """
            )
            params.extend([like, like, like, like, like])

        where_sql = " AND ".join(where_clauses)
        sort_sql = "sc.clicked_at DESC, sc.id DESC" if sort_filter == "newest" else "sc.clicked_at ASC, sc.id ASC"

        total_clicks = click_repository.count_clicks(where_sql, params)["total"]
        total_pages = max((total_clicks + per_page - 1) // per_page, 1)
        if page > total_pages:
            page = total_pages
        offset = (page - 1) * per_page

        rows = click_repository.get_clicks(where_sql, sort_sql, params, per_page, offset)

        click_events = []
        delete_forms = {}
        current_path = request.full_path.rstrip("?")
        for row in rows:
            row_dict = dict(row)
            row_dict["ip_masked"] = mask_ip(row["ip_address"])
            click_events.append(row_dict)
            delete_forms[row["id"]] = DeleteClickForm(click_id=str(row["id"]))

    except sqlite3.Error as e:
        current_app.logger.error(f"Erreur lors du chargement des clics admin: {e}")
        flash("Erreur lors du chargement des clics.", "error")
        click_events = []
        delete_forms = {}
        current_path = url_for("admin_clicks")
        total_clicks = 0
        total_pages = 1
        page = 1

    return render_template(
        "admin/clicks.html",
        click_events=click_events,
        delete_forms=delete_forms,
        query_text=query_text,
        sort_filter=sort_filter,
        days_filter=days_filter,
        page=page,
        total_pages=total_pages,
        total_clicks=total_clicks,
        return_to=current_path,
        admin_username=session.get("admin_username"),
    )


@admin_bp.route("/admin/clicks/<int:click_id>/delete", methods=["POST"])
@admin_required
def admin_delete_click(click_id):
    form = DeleteClickForm()
    if not form.validate_on_submit():
        flash("Formulaire invalide.", "error")
        return redirect(url_for("admin_clicks"))

    try:
        form_click_id = int(form.click_id.data)
    except (TypeError, ValueError):
        abort(400)

    if form_click_id != click_id:
        abort(400)

    return_to = request.form.get("return_to", "")
    if not is_safe_next_url(return_to):
        return_to = url_for("admin_clicks")

    try:
        click_row = click_repository.get_click_by_id(click_id)
        if not click_row:
            flash("Clic introuvable.", "error")
            return redirect(return_to)

        site_id = click_row["site_id"]
        deleted = click_repository.delete_click_and_decrement_site(click_id, site_id)
        if deleted == 0:
            flash("Clic introuvable.", "error")
            return redirect(return_to)

        flash("Événement de clic supprimé.", "success")
    except sqlite3.Error as e:
        current_app.logger.error(f"Erreur lors de la suppression du clic {click_id}: {e}")
        flash("Erreur lors de la suppression du clic.", "error")

    return redirect(return_to)


@admin_bp.route("/admin/categories", methods=["GET"])
@admin_required
def admin_categories():
    try:
        categories = category_repository.get_all_categories()
    except sqlite3.Error as e:
        current_app.logger.error(f"Erreur lors de la récupération des catégories: {e}")
        flash("Erreur lors du chargement des catégories.", "error")
        categories = []

    delete_forms = {cat["id"]: DeleteCategoryForm(category_id=str(cat["id"])) for cat in categories}

    return render_template(
        "admin/categories.html",
        categories_=categories,
        delete_forms=delete_forms,
        admin_username=session.get("admin_username"),
    )


@admin_bp.route("/admin/categories/new", methods=["GET", "POST"])
@admin_required
def admin_create_category():
    form = CategoryForm()
    if form.validate_on_submit():
        conn = get_db_connection()
        if not conn:
            flash("Impossible de se connecter à la base de données.", "error")
            return redirect(url_for("admin_categories"))
        try:
            cur = conn.cursor()
            if category_repository.get_category_by_name(form.nom.data):
                flash("Cette catégorie existe déjà.", "error")
                conn.close()
                return redirect(url_for("admin_categories"))

            slug = generate_unique_category_slug(cur, form.nom.data)
            conn.commit()
            category_repository.create_category(form.nom.data, slug)
            flash("Catégorie créée.", "success")
            return redirect(url_for("admin_categories"))
        except sqlite3.Error as e:
            conn.rollback()
            current_app.logger.error(f"Erreur lors de la création d'une catégorie: {e}")
            flash("Erreur lors de la création de la catégorie.", "error")
        finally:
            conn.close()

    return render_template(
        "admin/edit_category.html",
        form=form,
        admin_username=session.get("admin_username"),
        page_title="Créer une catégorie",
        submit_label="Créer la catégorie",
    )


@admin_bp.route("/admin/categories/<int:category_id>/edit", methods=["GET", "POST"])
@admin_required
def admin_edit_category(category_id):
    form = CategoryForm()
    conn = get_db_connection()
    if not conn:
        flash("Impossible de se connecter à la base de données.", "error")
        return redirect(url_for("admin_categories"))

    try:
        category = category_repository.get_category_by_id(category_id)
    except sqlite3.Error as e:
        conn.close()
        current_app.logger.error(f"Erreur lors du chargement de la catégorie {category_id}: {e}")
        flash("Impossible de charger la catégorie.", "error")
        return redirect(url_for("admin_categories"))

    if not category:
        conn.close()
        flash("Catégorie introuvable.", "error")
        return redirect(url_for("admin_categories"))

    if request.method == "GET":
        form.nom.data = category["nom"]
    elif form.validate_on_submit():
        try:
            cur = conn.cursor()
            if category_repository.get_category_by_name_excluding_id(form.nom.data, category_id):
                flash("Une autre catégorie porte déjà ce nom.", "error")
                conn.close()
                return redirect(url_for("admin_categories"))

            slug = generate_unique_category_slug(cur, form.nom.data, exclude_id=category_id)
            conn.commit()
            category_repository.update_category(category_id, form.nom.data, slug)
            flash("Catégorie mise à jour.", "success")
            conn.close()
            return redirect(url_for("admin_categories"))
        except sqlite3.Error as e:
            conn.rollback()
            conn.close()
            current_app.logger.error(f"Erreur lors de la mise à jour de la catégorie {category_id}: {e}")
            flash("Erreur lors de la mise à jour.", "error")
            return redirect(url_for("admin_categories"))

    conn.close()
    return render_template(
        "admin/edit_category.html",
        form=form,
        admin_username=session.get("admin_username"),
        page_title=f"Éditer la catégorie « {category['nom']} »",
        submit_label="Enregistrer",
    )


@admin_bp.route("/admin/categories/<int:category_id>/delete", methods=["POST"])
@admin_required
def admin_delete_category(category_id):
    form = DeleteCategoryForm()
    if not form.validate_on_submit():
        flash("Formulaire invalide.", "error")
        return redirect(url_for("admin_categories"))

    try:
        category_id_form = int(form.category_id.data)
    except (TypeError, ValueError):
        abort(400)

    if category_id != category_id_form:
        abort(400)

    conn = get_db_connection()
    if not conn:
        flash("Impossible de se connecter à la base de données.", "error")
        return redirect(url_for("admin_categories"))

    try:
        row = category_repository.get_category_by_id(category_id)
        if not row:
            flash("Catégorie introuvable.", "error")
            conn.close()
            return redirect(url_for("admin_categories"))

        usage = category_repository.count_sites_by_category(category_id)["total"]
        if usage > 0:
            flash("Impossible de supprimer : des sites utilisent encore cette catégorie.", "error")
            conn.close()
            return redirect(url_for("admin_categories"))

        category_repository.delete_category(category_id)
        flash("Catégorie supprimée.", "success")
    except sqlite3.Error as e:
        conn.rollback()
        current_app.logger.error(f"Erreur lors de la suppression de la catégorie {category_id}: {e}")
        flash("Erreur lors de la suppression.", "error")
    finally:
        conn.close()

    return redirect(url_for("admin_categories"))


@admin_bp.route("/admin/propositions/<int:site_id>", methods=["POST"])
@admin_required
def admin_update_site(site_id):
    form = ModerationActionForm()
    return_to = form.return_to.data if is_safe_next_url(form.return_to.data or "") else url_for("admin_dashboard")
    if not form.validate_on_submit():
        current_app.logger.warning(f"Modération formulaire invalide: {form.errors}")
        flash("Formulaire invalide.", "error")
        return redirect(return_to)

    try:
        site_id_form = int(form.site_id.data)
    except (TypeError, ValueError):
        abort(400)

    if site_id_form != site_id:
        abort(400)

    action = request.form.get("action")
    if action not in {"approve", "reject", "delete", "pending"}:
        flash("Action inconnue.", "error")
        return redirect(return_to)

    message = ""
    try:
        if action == "approve":
            rowcount = site_repository.update_site_status(site_id, "valide", refresh_date=True)
            message = "Proposition validée et publiée."
        elif action == "reject":
            rowcount = site_repository.update_site_status(site_id, "refuse")
            message = "Proposition refusée."
        elif action == "pending":
            rowcount = site_repository.update_site_status(site_id, "en_attente")
            message = "Statut remis en attente."
        else:
            rowcount = site_repository.delete_site(site_id)
            message = "Proposition supprimée."

        if rowcount == 0:
            flash("Proposition introuvable.", "error")
        else:
            flash(message, "success")
    except sqlite3.Error as e:
        current_app.logger.error(f"Erreur lors de la mise à jour de la proposition {site_id}: {e}")
        flash("Erreur lors de la mise à jour de la proposition.", "error")

    return redirect(return_to)


@admin_bp.route("/admin/propositions/<int:site_id>/edit", methods=["GET", "POST"])
@admin_required
def admin_edit_site(site_id):
    try:
        site = site_repository.get_site_by_id(site_id)
    except sqlite3.Error as e:
        current_app.logger.error(f"Erreur lors de la récupération du site {site_id}: {e}")
        flash("Impossible de charger la proposition.", "error")
        return redirect(url_for("admin_dashboard"))

    if not site:
        flash("Proposition introuvable.", "error")
        return redirect(url_for("admin_dashboard"))

    form = AdminSiteForm()
    form.honeypot.data = ""
    categories_list = get_categories()
    form.categorie.choices = [(cat, cat) for cat in categories_list]
    form.categorie.choices.insert(0, ("", "Sélectionnez une catégorie"))
    form.ville.choices = get_city_choices()
    posted_category = request.form.get("categorie")
    posted_ville = request.form.get("ville")
    if posted_category and posted_category not in [choice[0] for choice in form.categorie.choices]:
        form.categorie.choices.append((posted_category, posted_category))
    if posted_ville and posted_ville not in [choice[0] for choice in form.ville.choices]:
        form.ville.choices.append((posted_ville, posted_ville))

    if request.method == "GET":
        form.nom.data = site["nom"]
        if site["ville"] and site["ville"] not in [choice[0] for choice in form.ville.choices]:
            form.ville.choices.append((site["ville"], site["ville"]))
        form.ville.data = site["ville"] or ""
        form.lien.data = site["lien"]
        form.description.data = site["description"]
        form.status.data = site["status"]
        form.en_vedette.data = bool(site["en_vedette"])
        current_category = site["categorie"] or ""
        if current_category and current_category not in categories_list:
            form.categorie.choices.append((current_category, current_category))
        form.categorie.data = current_category
    elif form.validate_on_submit():
        conn_to_update = get_db_connection()
        if not conn_to_update:
            flash("Impossible de se connecter à la base de données.", "error")
            return redirect(url_for("admin_dashboard"))
        # Sécurise la catégorie envoyée (doit exister)
        if form.categorie.data not in [choice[0] for choice in form.categorie.choices if choice[0]]:
            flash("Catégorie non valide.", "error")
            conn_to_update.close()
            return redirect(url_for("admin_dashboard"))
        try:
            cur_update = conn_to_update.cursor()
            resolved = resolve_category(cur_update, form.categorie.data)
            if not resolved:
                flash("Catégorie non valide.", "error")
                conn_to_update.rollback()
                conn_to_update.close()
                return redirect(url_for("admin_dashboard"))
            resolved_category_id, _resolved_category_name = resolved
            resolved_city = resolve_city(cur_update, form.ville.data)
            if (form.ville.data or "").strip() and not resolved_city:
                flash("Ville non valide.", "error")
                conn_to_update.rollback()
                conn_to_update.close()
                return redirect(url_for("admin_dashboard"))
            resolved_city_id = resolved_city[0] if resolved_city else None
            conn_to_update.commit()
            rowcount = site_repository.update_site(
                site_id,
                form.nom.data,
                resolved_city_id,
                form.lien.data,
                form.description.data,
                resolved_category_id,
                form.status.data,
                1 if form.en_vedette.data else 0,
            )
            if rowcount == 0:
                flash("La mise à jour a échoué : proposition introuvable.", "error")
            else:
                flash("Proposition mise à jour avec succès.", "success")
            conn_to_update.close()
            return redirect(url_for("admin_dashboard"))
        except sqlite3.Error as e:
            conn_to_update.rollback()
            conn_to_update.close()
            current_app.logger.error(f"Erreur lors de la mise à jour du site {site_id}: {e}")
            flash("Erreur lors de la mise à jour.", "error")
            return redirect(url_for("admin_dashboard"))
    else:
        flash("Formulaire invalide.", "error")

    return render_template(
        "admin/edit_site.html",
        form=form,
        site=site,
        admin_username=session.get("admin_username"),
        form_action=url_for("admin_edit_site", site_id=site_id),
        submit_label="Enregistrer les modifications",
        page_title=f"Modifier la proposition #{site_id}",
        subtitle=f"Statut actuel : <strong>{site['status']}</strong>",
    )


@admin_bp.route("/admin/propositions/new", methods=["GET", "POST"])
@admin_required
def admin_create_site():
    form = AdminSiteForm()
    form.honeypot.data = ""
    categories_list = get_categories()
    form.categorie.choices = [(cat, cat) for cat in categories_list]
    form.categorie.choices.insert(0, ("", "Sélectionnez une catégorie"))
    form.ville.choices = get_city_choices()
    posted_category = request.form.get("categorie")
    posted_ville = request.form.get("ville")
    if posted_category and posted_category not in [choice[0] for choice in form.categorie.choices]:
        form.categorie.choices.append((posted_category, posted_category))
    if posted_ville and posted_ville not in [choice[0] for choice in form.ville.choices]:
        form.ville.choices.append((posted_ville, posted_ville))

    if form.validate_on_submit():
        if form.categorie.data not in [choice[0] for choice in form.categorie.choices if choice[0]]:
            flash("Catégorie non valide.", "error")
            return redirect(url_for("admin_create_site"))
        conn = get_db_connection()
        if not conn:
            flash("Impossible de se connecter à la base de données.", "error")
            return redirect(url_for("admin_dashboard"))
        try:
            cur = conn.cursor()
            resolved = resolve_category(cur, form.categorie.data)
            if not resolved:
                flash("Catégorie non valide.", "error")
                return redirect(url_for("admin_create_site"))
            resolved_category_id, _resolved_category_name = resolved
            resolved_city = resolve_city(cur, form.ville.data)
            if (form.ville.data or "").strip() and not resolved_city:
                flash("Ville non valide.", "error")
                return redirect(url_for("admin_create_site"))
            resolved_city_id = resolved_city[0] if resolved_city else None
            conn.commit()
            site_repository.create_site(
                form.nom.data,
                resolved_city_id,
                form.lien.data,
                form.description.data,
                resolved_category_id,
                status=form.status.data or "valide",
                en_vedette=1 if form.en_vedette.data else 0,
            )
            flash(f"Nouveau site ajouté (statut : {form.status.data}).", "success")
            return redirect(url_for("admin_dashboard"))
        except sqlite3.Error as e:
            conn.rollback()
            current_app.logger.error(f"Erreur lors de la création d'un site depuis l'admin: {e}")
            flash("Erreur lors de l'ajout du site.", "error")
        finally:
            conn.close()

    return render_template(
        "admin/edit_site.html",
        form=form,
        site=None,
        admin_username=session.get("admin_username"),
        form_action=url_for("admin_create_site"),
        submit_label="Publier le site",
        page_title="Ajouter un nouveau site",
        subtitle="Complète les champs pour publier le site instantanément.",
    )
