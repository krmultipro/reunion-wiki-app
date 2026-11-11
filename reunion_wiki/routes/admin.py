from datetime import datetime
import sqlite3

from flask import Blueprint, abort, current_app, flash, redirect, render_template, request, session, url_for

from ..auth import admin_required, verify_admin_credentials
from ..extensions import limiter
from ..forms.auth_forms import AdminLoginForm, AdminLogoutForm
from ..forms.category_forms import CategoryForm, DeleteCategoryForm
from ..forms.click_forms import CorrectAggregateForm
from ..forms.site_forms import AdminSiteForm, EditorialReviewForm, ManualHttpReviewForm, ModerationActionForm
from ..repositories import category_repository, city_repository, click_repository, site_refusal_repository, site_repository
from ..services import (
    category_service,
    city_service,
    site_lifecycle_service,
    site_location_service,
    site_publication_service,
    site_url_service,
)
from ..utils import is_safe_next_url, parse_positive_int


admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/admin/login", methods=["GET", "POST"])
@limiter.limit("5 per minute")
def admin_login():
    form = AdminLoginForm()
    next_url = request.args.get("next")
    if not is_safe_next_url(next_url):
        next_url = url_for("refonte_submission.admin_index")

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
        refusal_history=site_refusal_repository.get_latest_refusals(site["id"] for site in pending_sites),
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

    allowed_status = {"all", "draft", "valide", "en_attente", "refuse", "archived"}
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
        cities = city_repository.get_all_cities()

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
        refusal_history=site_refusal_repository.get_latest_refusals(site["id"] for site in all_sites),
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
    days_filter = parse_positive_int(request.args.get("days"), default=30)
    if days_filter not in {1, 7, 30, 90, 365}:
        days_filter = 30
    try:
        geo_stats = click_repository.get_admin_geo_stats(days_filter, privacy_threshold=10)
        aggregate_rows = click_repository.get_geo_aggregate_rows(days_filter)
    except sqlite3.Error as e:
        current_app.logger.error(f"Erreur lors du chargement des agrégats: {e}")
        geo_stats, aggregate_rows = [], []
    correction_forms = {}
    for row in aggregate_rows:
        key = (row["site_id"], row["stat_date"], row["zone"])
        correction_forms[key] = CorrectAggregateForm(
            site_id=str(row["site_id"]), stat_date=row["stat_date"], zone=row["zone"]
        )
    return render_template(
        "admin/clicks_aggregated.html", geo_stats=geo_stats,
        aggregate_rows=aggregate_rows, correction_forms=correction_forms,
        days_filter=days_filter, admin_username=session.get("admin_username"),
    )


@admin_bp.route("/admin/clicks/aggregate-correction", methods=["POST"])
@admin_required
def admin_correct_click_aggregate():
    """Corrige un compteur agrégé et conserve une trace administrative."""
    form = CorrectAggregateForm()
    if not form.validate_on_submit():
        flash("Correction invalide.", "error")
        return redirect(url_for("admin_clicks"))
    corrected = click_repository.correct_geo_aggregate(
        int(form.site_id.data), form.stat_date.data, form.zone.data,
        form.new_count.data, session.get("admin_username") or "admin", form.reason.data,
    )
    flash("Compteur agrégé corrigé." if corrected else "Agrégat introuvable.",
          "success" if corrected else "error")
    return redirect(url_for("admin_clicks"))


@admin_bp.route("/admin/clicks/legacy", methods=["GET"])
@admin_required
def admin_clicks_legacy_disabled():
    """Empêche l'affichage des anciens événements individuels."""
    abort(404)


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
        try:
            if category_repository.get_category_by_name(form.nom.data):
                flash("Cette catégorie existe déjà.", "error")
                return redirect(url_for("admin_categories"))

            slug = category_service.generate_unique_slug(form.nom.data)
            category_repository.create_category(form.nom.data, slug)
            flash("Catégorie créée.", "success")
            return redirect(url_for("admin_categories"))
        except sqlite3.Error as e:
            current_app.logger.error(f"Erreur lors de la création d'une catégorie: {e}")
            flash("Erreur lors de la création de la catégorie.", "error")

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

    try:
        category = category_repository.get_category_by_id(category_id)
    except sqlite3.Error as e:
        current_app.logger.error(f"Erreur lors du chargement de la catégorie {category_id}: {e}")
        flash("Impossible de charger la catégorie.", "error")
        return redirect(url_for("admin_categories"))

    if not category:
        flash("Catégorie introuvable.", "error")
        return redirect(url_for("admin_categories"))

    if request.method == "GET":
        form.nom.data = category["nom"]
    elif form.validate_on_submit():
        try:
            if category_repository.get_category_by_name_excluding_id(form.nom.data, category_id):
                flash("Une autre catégorie porte déjà ce nom.", "error")
                return redirect(url_for("admin_categories"))

            slug = category_service.generate_unique_slug(
                form.nom.data,
                exclude_id=category_id,
            )
            category_repository.update_category(category_id, form.nom.data, slug)
            flash("Catégorie mise à jour.", "success")
            return redirect(url_for("admin_categories"))
        except sqlite3.Error as e:
            current_app.logger.error(f"Erreur lors de la mise à jour de la catégorie {category_id}: {e}")
            flash("Erreur lors de la mise à jour.", "error")
            return redirect(url_for("admin_categories"))

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

    try:
        row = category_repository.get_category_by_id(category_id)
        if not row:
            flash("Catégorie introuvable.", "error")
            return redirect(url_for("admin_categories"))

        usage = category_repository.count_sites_by_category(category_id)["total"]
        if usage > 0:
            flash("Impossible de supprimer : des sites utilisent encore cette catégorie.", "error")
            return redirect(url_for("admin_categories"))

        category_repository.delete_category(category_id)
        flash("Catégorie supprimée.", "success")
    except sqlite3.Error as e:
        current_app.logger.error(f"Erreur lors de la suppression de la catégorie {category_id}: {e}")
        flash("Erreur lors de la suppression.", "error")

    return redirect(url_for("admin_categories"))


@admin_bp.route("/admin/propositions/<int:site_id>", methods=["POST"])
@admin_required
def admin_update_site(site_id):
    form = ModerationActionForm()
    return_to = form.return_to.data if is_safe_next_url(form.return_to.data or "") else url_for("admin_dashboard")
    if not form.validate_on_submit():
        current_app.logger.warning(f"Modération formulaire invalide: {form.errors}")
        flash("Choisissez un motif de refus valide." if form.refusal_reason.errors else "Formulaire invalide.", "error")
        return redirect(return_to)

    try:
        site_id_form = int(form.site_id.data)
    except (TypeError, ValueError):
        abort(400)

    if site_id_form != site_id:
        abort(400)

    action = request.form.get("action")
    if action not in {"approve", "reject", "delete", "pending", "archive"}:
        flash("Action inconnue.", "error")
        return redirect(return_to)

    message = ""
    try:
        if action == "approve":
            existing = site_repository.get_site_by_id(site_id)
            if not existing:
                flash("Proposition introuvable.", "error")
                return redirect(return_to)
            if not site_lifecycle_service.can_transition(existing["status"], "valide"):
                flash("Transition de statut non autorisée.", "error")
                return redirect(return_to)
            return redirect(url_for("admin.admin_editorial_review", site_id=site_id))
        elif action == "reject":
            decision = site_lifecycle_service.transition_status(
                site_id, "refuse", refusal_reason=form.refusal_reason.data,
                admin_username=session.get("admin_username") or "admin",
            )
        elif action == "pending":
            decision = site_lifecycle_service.transition_status(site_id, "en_attente")
        elif action == "archive":
            decision = site_lifecycle_service.transition_status(site_id, "archived")
        else:
            rowcount = site_repository.delete_site(site_id)
            message = "Proposition supprimée."

        if action in {"reject", "pending", "archive"}:
            flash(decision.message, decision.category)
        elif rowcount == 0:
            flash("Proposition introuvable.", "error")
        else:
            flash(message, "success")
    except sqlite3.Error as e:
        current_app.logger.error(f"Erreur lors de la mise à jour de la proposition {site_id}: {e}")
        flash("Erreur lors de la mise à jour de la proposition.", "error")

    return redirect(return_to)


@admin_bp.route(
    "/admin/propositions/<int:site_id>/editorial-review",
    methods=["GET", "POST"],
)
@admin_required
def admin_editorial_review(site_id):
    """Record a human eligibility decision before any publication attempt."""
    site = site_repository.get_site_by_id(site_id)
    if not site or not site_lifecycle_service.can_transition(site["status"], "valide"):
        flash("Ce site n'est pas en attente de publication.", "error")
        return redirect(url_for("admin_dashboard"))

    form = EditorialReviewForm()
    if request.method == "GET":
        form.reviewed_url.data = site["lien"]
    elif form.validate_on_submit():
        attempt = site_publication_service.review_and_attempt_publication(
            site_id, form.reviewed_url.data, form.criterion.data,
            form.note.data, form.evidence_url.data,
            session.get("admin_username") or "admin",
            new_publication=site["status"] == "archived" and request.args.get("new_publication") == "1",
        )
        flash(attempt.message, attempt.category)
        if attempt.manual_check_id:
            return redirect(url_for("admin_http_review", site_id=site_id, check_id=attempt.manual_check_id))
        return redirect(url_for("admin_dashboard"))

    return render_template(
        "admin/editorial_review.html", form=form, site=site,
        admin_username=session.get("admin_username"),
    )


@admin_bp.route(
    "/admin/propositions/<int:site_id>/http-review/<int:check_id>",
    methods=["GET", "POST"],
)
@admin_required
def admin_http_review(site_id, check_id):
    """Confirme manuellement un site ayant répondu 401 ou 403."""
    review = site_publication_service.get_manual_review(check_id, site_id)
    if not review:
        flash("Cette vérification manuelle n'est plus valable.", "error")
        return redirect(url_for("admin_dashboard"))

    form = ManualHttpReviewForm()
    if request.method == "GET":
        form.site_id.data = str(site_id)
        form.check_id.data = str(check_id)
    elif form.validate_on_submit():
        try:
            submitted_site_id = int(form.site_id.data)
            submitted_check_id = int(form.check_id.data)
        except (TypeError, ValueError):
            abort(400)
        if submitted_site_id != site_id or submitted_check_id != check_id:
            abort(400)

        if site_publication_service.confirm_manual_publication(
            site_id,
            check_id,
            session.get("admin_username") or "admin",
            form.note.data,
        ):
            flash("Vérification manuelle enregistrée et site publié.", "success")
            return redirect(url_for("admin_dashboard"))
        flash("La confirmation n'est plus valable. Vérifiez à nouveau le site.", "error")
        return redirect(url_for("admin_dashboard"))

    return render_template(
        "admin/http_review.html",
        form=form,
        review=review,
        admin_username=session.get("admin_username"),
    )


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
    allowed_edit_statuses = {site["status"], *site_lifecycle_service.allowed_targets(site["status"])}
    form.status.choices = [
        (key, label) for key, label in site_lifecycle_service.STATUS_LABELS.items()
        if key in allowed_edit_statuses
    ]
    if request.method == "POST" and request.form.get("status") not in allowed_edit_statuses:
        flash("Transition de statut non autorisée.", "error")
        return redirect(url_for("admin_edit_site", site_id=site_id))
    categories_list = category_service.get_category_names()
    form.categorie.choices = [(cat, cat) for cat in categories_list]
    form.categorie.choices.insert(0, ("", "Sélectionnez une catégorie"))
    form.ville.choices = city_service.get_name_choices()
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
        form.portee.data = site["location_scope"] or ""
        form.status.data = site["status"]
        form.en_vedette.data = bool(site["en_vedette"])
        current_category = site["categorie"] or ""
        if current_category and current_category not in categories_list:
            form.categorie.choices.append((current_category, current_category))
        form.categorie.data = current_category
    elif form.validate_on_submit():
        # Sécurise la catégorie envoyée (doit exister)
        if form.categorie.data not in [choice[0] for choice in form.categorie.choices if choice[0]]:
            flash("Catégorie non valide.", "error")
            return redirect(url_for("admin_dashboard"))
        try:
            resolved = category_service.resolve_category(form.categorie.data)
            if not resolved:
                flash("Catégorie non valide.", "error")
                return redirect(url_for("admin_dashboard"))
            resolved_category_id, _resolved_category_name = resolved
            resolved_city = city_service.resolve_city(form.ville.data)
            if (form.ville.data or "").strip() and not resolved_city:
                flash("Ville non valide.", "error")
                return redirect(url_for("admin_dashboard"))
            resolved_city_id = resolved_city[0] if resolved_city else None
            location_scope = site_location_service.validate_location(
                resolved_city_id, form.portee.data
            )
            url_decision = site_url_service.prepare_site_url(
                form.lien.data, exclude_site_id=site_id
            )
            requested_status = form.status.data
            if form.new_publication.data and not (
                site["status"] == "archived" and requested_status == "valide"
            ):
                flash("La nouvelle publication exige un site archivé.", "error")
                return redirect(url_for("admin_edit_site", site_id=site_id))
            stored_status, needs_review, status_error = site_lifecycle_service.edit_status(
                site["status"], requested_status,
                url_changed=url_decision.normalized_url != site["lien"],
            )
            if status_error:
                flash(status_error, "error")
                return redirect(url_for("admin_edit_site", site_id=site_id))
            rowcount = site_repository.update_site(
                site_id,
                form.nom.data,
                resolved_city_id,
                url_decision.normalized_url,
                form.description.data,
                resolved_category_id,
                stored_status,
                1 if form.en_vedette.data else 0,
                expected_status=site["status"],
                location_scope=location_scope,
                refusal_reason=form.refusal_reason.data,
                admin_username=session.get("admin_username") or "admin",
            )
            if rowcount == 0:
                flash("La proposition a changé ou est introuvable. Actualisez la page.", "error")
            else:
                flash("Proposition mise à jour avec succès.", "success")
                if url_decision.warning:
                    flash(url_decision.warning, "warning")
                if needs_review:
                    return redirect(url_for(
                        "admin.admin_editorial_review", site_id=site_id,
                        new_publication="1" if form.new_publication.data else "0",
                    ))
            return redirect(url_for("admin_dashboard"))
        except site_url_service.DuplicateSiteUrlError as e:
            form.lien.errors.append(str(e))
            flash(str(e), "error")
        except site_refusal_repository.InvalidRefusalReason as e:
            form.refusal_reason.errors.append(str(e))
            flash(str(e), "error")
        except ValueError as e:
            form.portee.errors.append(str(e))
            flash(str(e), "error")
        except sqlite3.Error as e:
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
        last_refusal=site_refusal_repository.get_latest_refusal(site_id),
    )


@admin_bp.route("/admin/propositions/new", methods=["GET", "POST"])
@admin_required
def admin_create_site():
    form = AdminSiteForm()
    form.honeypot.data = ""
    form.status.choices = [("draft", "Brouillon"), ("valide", "Publié")]
    if request.method == "POST" and request.form.get("status") not in {"draft", "valide"}:
        flash("Un nouveau site administratif doit commencer en brouillon ou passer par la publication.", "error")
        return redirect(url_for("admin_create_site"))
    categories_list = category_service.get_category_names()
    form.categorie.choices = [(cat, cat) for cat in categories_list]
    form.categorie.choices.insert(0, ("", "Sélectionnez une catégorie"))
    form.ville.choices = city_service.get_name_choices()
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
        try:
            resolved = category_service.resolve_category(form.categorie.data)
            if not resolved:
                flash("Catégorie non valide.", "error")
                return redirect(url_for("admin_create_site"))
            resolved_category_id, _resolved_category_name = resolved
            resolved_city = city_service.resolve_city(form.ville.data)
            if (form.ville.data or "").strip() and not resolved_city:
                flash("Ville non valide.", "error")
                return redirect(url_for("admin_create_site"))
            resolved_city_id = resolved_city[0] if resolved_city else None
            location_scope = site_location_service.validate_location(
                resolved_city_id, form.portee.data
            )
            url_decision = site_url_service.prepare_site_url(form.lien.data)
            requested_status = form.status.data
            stored_status = "draft"
            site_id = site_repository.create_site(
                form.nom.data,
                resolved_city_id,
                url_decision.normalized_url,
                form.description.data,
                resolved_category_id,
                status=stored_status,
                en_vedette=1 if form.en_vedette.data else 0,
                location_scope=location_scope,
            )
            flash(f"Nouveau site ajouté (statut : {stored_status}).", "success")
            if url_decision.warning:
                flash(url_decision.warning, "warning")
            if requested_status == "valide":
                return redirect(url_for("admin.admin_editorial_review", site_id=site_id))
            return redirect(url_for("admin_dashboard"))
        except site_url_service.DuplicateSiteUrlError as e:
            form.lien.errors.append(str(e))
            flash(str(e), "error")
        except ValueError as e:
            form.portee.errors.append(str(e))
            flash(str(e), "error")
        except sqlite3.Error as e:
            current_app.logger.error(f"Erreur lors de la création d'un site depuis l'admin: {e}")
            flash("Erreur lors de l'ajout du site.", "error")

    return render_template(
        "admin/edit_site.html",
        form=form,
        site=None,
        admin_username=session.get("admin_username"),
        form_action=url_for("admin_create_site"),
        submit_label="Enregistrer le site",
        page_title="Ajouter un nouveau site",
        subtitle="Enregistre un brouillon ou lance la revue avant publication.",
    )
