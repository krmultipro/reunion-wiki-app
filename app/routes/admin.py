"""Administration routes (dashboard, moderation, talents)."""

from __future__ import annotations

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

from ..database import DatabaseError, db_transaction
from ..extensions import limiter
from ..forms import (
    AdminLoginForm,
    ModerationActionForm,
    SiteForm,
    TalentAdminForm,
    TalentModerationActionForm,
)
from ..services.auth import admin_required, verify_admin_credentials
from ..services.sites import (
    create_site_admin,
    get_admin_sites,
    get_categories,
    get_site_by_id,
    move_site_order,
    update_site_full,
    update_site_status,
    delete_site,
)
from ..services.talents import (
    TALENT_STATUSES,
    TALENT_STATUS_LABELS,
    create_talent_admin,
    get_admin_talents,
    get_talent_by_id,
    get_talent_category_choices,
    get_talent_status_choices,
    move_talent_order,
    update_talent_full,
    update_talent_status,
    delete_talent,
)

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def log_admin_login_attempt(username: str, success: bool) -> None:
    """Persist admin login attempts for audit purposes."""
    ip_address = request.remote_addr or "IP inconnue"
    user_agent = request.user_agent.string if request.user_agent else ""
    user_agent = user_agent[:255]
    try:
        with db_transaction() as conn:
            conn.execute(
                """
                INSERT INTO login_attempts (username, ip, success, user_agent)
                VALUES (?, ?, ?, ?)
                """,
                (username, ip_address, 1 if success else 0, user_agent),
            )
    except DatabaseError:
        current_app.logger.warning(
            "Impossible d'enregistrer la tentative de connexion admin pour '%s' (%s).",
            username,
            ip_address,
        )


@admin_bp.route("/login", methods=["GET", "POST"])
@limiter.limit("5 per minute")
def login():
    form = AdminLoginForm()
    next_url = request.args.get("next")
    if not next_url or not next_url.startswith("/"):
        next_url = url_for("admin.dashboard")

    if form.validate_on_submit():
        if verify_admin_credentials(form.username.data, form.password.data):
            log_admin_login_attempt(form.username.data, True)
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
        log_admin_login_attempt(form.username.data, False)
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
    status_filter = request.args.get("status", "en_attente")[:50]
    search_query = request.args.get("q", "").strip()[:100]
    sort_by = request.args.get("sort_by", "date_ajout")[:50]
    sort_order = request.args.get("sort_order", "desc")[:10]
    category_filter = request.args.get("category", "").strip()[:100] or None

    try:
        data = get_admin_sites(
            status_filter=status_filter, 
            search_query=search_query,
            sort_by=sort_by,
            sort_order=sort_order,
            category_filter=category_filter
        )
        entries = data["entries"]
        stats = data["stats"]
        category_stats = data.get("category_stats", {})
    except DatabaseError:
        flash("Impossible de se connecter à la base de données.", "error")
        return redirect(url_for("public.accueil"))

    action_forms = {}
    for site in entries:
        form = ModerationActionForm()
        form.site_id.data = str(site["id"])
        action_forms[site["id"]] = form

    try:
        categories_list = get_categories()
    except Exception:
        categories_list = []

    return render_template(
        "admin/dashboard.html",
        entries=entries,
        stats=stats,
        category_stats=category_stats or {},
        categories=categories_list or [],
        status_filter=status_filter,
        search_query=search_query or "",
        category_filter=category_filter or "",
        sort_by=sort_by or "date_ajout",
        sort_order=sort_order or "desc",
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

    try:
        if action == "approve":
            success, message = update_site_status(site_id, "valide")
        elif action == "reject":
            success, message = update_site_status(site_id, "refuse")
        else:
            success, message = delete_site(site_id)

        if success:
            current_app.logger.info(
                "Action admin '%s' sur proposition #%s par '%s' (%s)",
                action,
                site_id,
                session.get("admin_username") or "inconnu",
                request.remote_addr or "IP inconnue",
            )
            flash(message, "success")
        else:
            flash(message, "error")
    except DatabaseError:
        flash("Erreur lors de la mise à jour.", "error")

    category_redirect = request.form.get("category_filter", "")
    sort_by_redirect = request.form.get("sort_by", "date_ajout")
    sort_order_redirect = request.form.get("sort_order", "desc")

    return redirect(
        url_for("admin.dashboard", status=status_redirect, category=category_redirect, q=query_redirect, sort_by=sort_by_redirect, sort_order=sort_order_redirect)
    )


@admin_bp.route("/sites/<int:site_id>/move/<direction>", methods=["POST"])
@admin_required
def move_site(site_id: int, direction: str):
    """Move a site up or down in display order."""
    # Limite de longueur du paramètre direction (sécurité)
    direction = direction[:10]
    if direction not in ["up", "down"]:
        flash("Direction invalide.", "error")
        return redirect(url_for("admin.dashboard"))
    
    status_filter = request.args.get("status", "en_attente")[:50]
    category_filter = request.args.get("category", "").strip()[:100] or None
    search_query = request.args.get("q", "").strip()[:100]
    sort_by = request.args.get("sort_by", "date_ajout")[:50]
    sort_order = request.args.get("sort_order", "desc")[:10]
    
    try:
        success, message = move_site_order(site_id, direction, category=category_filter)
        if success:
            flash(message, "success")
        else:
            flash(message, "error")
    except DatabaseError:
        flash("Erreur lors du déplacement du site.", "error")
    
    return redirect(url_for("admin.dashboard", status=status_filter, category=category_filter or "", q=search_query, sort_by=sort_by, sort_order=sort_order))


@admin_bp.route("/propositions/<int:site_id>/edit", methods=["GET", "POST"])
@admin_required
def edit_site(site_id: int):
    status_filter = request.args.get("status", "en_attente")[:50]
    category_filter = request.args.get("category", "").strip()[:100] or None
    search_query = request.args.get("q", "").strip()[:100]
    sort_by = request.args.get("sort_by", "date_ajout")[:50]
    sort_order = request.args.get("sort_order", "desc")[:10]
    
    form = SiteForm()
    form.honeypot.data = ""
    categories_list = get_categories()
    form.categorie.choices = [(cat, cat) for cat in categories_list]
    form.categorie.choices.insert(0, ("", "Sélectionnez une catégorie"))

    try:
        site = get_site_by_id(site_id)
    except DatabaseError:
        flash("Erreur lors de la récupération.", "error")
        return redirect(url_for("admin.dashboard", status=status_filter, category=category_filter or "", q=search_query, sort_by=sort_by, sort_order=sort_order))

    if not site:
        flash("Proposition introuvable.", "error")
        return redirect(url_for("admin.dashboard", status=status_filter, category=category_filter or "", q=search_query, sort_by=sort_by, sort_order=sort_order))

    if request.method == "GET":
        form.nom.data = site["nom"]
        form.ville.data = site["ville"] or ""
        form.lien.data = site["lien"]
        form.description.data = site["description"]
        form.categorie.data = site["categorie"] or ""

    if form.validate_on_submit():
        try:
            status = request.form.get("status") or site["status"]
            display_order = site.get("display_order", 0) or 0
            success, message = update_site_full(
                site_id=site_id,
                nom=form.nom.data,
                ville=form.ville.data or None,
                lien=form.lien.data,
                description=form.description.data,
                categorie=form.categorie.data,
                status=status,
                display_order=display_order,
            )
            if success:
                current_app.logger.info(
                    "Mise à jour admin de la proposition #%s par '%s' (%s)",
                    site_id,
                    session.get("admin_username") or "inconnu",
                    request.remote_addr or "IP inconnue",
                )
                flash(message, "success")
                return redirect(url_for("admin.dashboard", status=status_filter, category=category_filter or "", q=search_query, sort_by=sort_by, sort_order=sort_order))
            else:
                flash(message, "error")
        except DatabaseError:
            flash("Erreur lors de la mise à jour.", "error")

    return render_template(
        "admin/edit_site.html",
        form=form,
        site=site,
        admin_username=session.get("admin_username"),
        form_action=url_for(
            "admin.edit_site",
            site_id=site_id,
            status=status_filter,
            category=category_filter or "",
            q=search_query,
            sort_by=sort_by,
            sort_order=sort_order,
        ),
        submit_label="Enregistrer les modifications",
        page_title=f"Modifier la proposition #{site_id}",
        subtitle=f"Statut actuel : <strong>{site['status']}</strong>",
        status_filter=status_filter,
        category_filter=category_filter or "",
        search_query=search_query,
        sort_by=sort_by,
        sort_order=sort_order,
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
        try:
            success, message = create_site_admin(
                nom=form.nom.data,
                ville=form.ville.data or None,
                lien=form.lien.data,
                description=form.description.data,
                categorie=form.categorie.data,
                display_order=0,
            )
            if success:
                current_app.logger.info(
                    "Création admin d'un site (%s) par '%s' (%s)",
                    form.lien.data,
                    session.get("admin_username") or "inconnu",
                    request.remote_addr or "IP inconnue",
                )
                flash(message, "success")
                return redirect(url_for("admin.dashboard"))
            else:
                flash(message, "error")
        except DatabaseError:
            flash("Erreur lors de l'ajout du site.", "error")

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
    status_filter = request.args.get("status", "en_attente")[:50]
    search_query = request.args.get("q", "").strip()[:100]
    sort_by = request.args.get("sort_by", "date_updated")[:50]
    sort_order = request.args.get("sort_order", "desc")[:10]
    category_filter = request.args.get("category", "").strip()[:100] or None

    try:
        data = get_admin_talents(
            status_filter=status_filter, 
            search_query=search_query,
            sort_by=sort_by,
            sort_order=sort_order,
            category_filter=category_filter
        )
        entries = data["entries"]
        stats = data["stats"]
        category_stats = data.get("category_stats", {})
    except DatabaseError:
        flash("Impossible de se connecter à la base de données.", "error")
        return redirect(url_for("admin.dashboard"))

    action_forms = {}
    for talent in entries:
        form = TalentModerationActionForm()
        form.talent_id.data = str(talent["id"])
        action_forms[talent["id"]] = form

    from ..services.talents import TALENT_CATEGORIES

    return render_template(
        "admin/talents.html",
        entries=entries,
        stats=stats,
        category_stats=category_stats,
        categories=TALENT_CATEGORIES,
        status_filter=status_filter,
        search_query=search_query,
        category_filter=category_filter or "",
        sort_by=sort_by,
        sort_order=sort_order,
        action_forms=action_forms,
        admin_username=session.get("admin_username"),
        status_labels=TALENT_STATUS_LABELS,
    )


@admin_bp.route("/talents/<int:talent_id>", methods=["POST"])
@admin_required
def update_talent(talent_id: int):
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

    try:
        if action == "approve":
            success, message = update_talent_status(talent_id, "valide")
        elif action == "reject":
            success, message = update_talent_status(talent_id, "refuse")
        else:
            success, message = delete_talent(talent_id)

        if success:
            current_app.logger.info(
                "Action admin '%s' sur talent #%s par '%s' (%s)",
                action,
                talent_id,
                session.get("admin_username") or "inconnu",
                request.remote_addr or "IP inconnue",
            )
            flash(message, "success")
        else:
            flash(message, "error")
    except DatabaseError:
        flash("Erreur lors de la mise à jour du talent.", "error")

    return redirect(url_for("admin.talents", status=status_redirect, q=query_redirect))


@admin_bp.route("/talents/<int:talent_id>/move/<direction>", methods=["POST"])
@admin_required
def move_talent(talent_id: int, direction: str):
    """Move a talent up or down in display order."""
    # Limite de longueur du paramètre direction (sécurité)
    direction = direction[:10]
    if direction not in ["up", "down"]:
        flash("Direction invalide.", "error")
        return redirect(url_for("admin.talents"))
    
    status_filter = request.args.get("status", "en_attente")[:50]
    category_filter = request.args.get("category", "").strip()[:100] or None
    search_query = request.args.get("q", "").strip()[:100]
    sort_by = request.args.get("sort_by", "date_updated")[:50]
    sort_order = request.args.get("sort_order", "desc")[:10]
    
    try:
        success, message = move_talent_order(talent_id, direction, category=category_filter)
        if success:
            flash(message, "success")
        else:
            flash(message, "error")
    except DatabaseError:
        flash("Erreur lors du déplacement du talent.", "error")
    
    return redirect(url_for("admin.talents", status=status_filter, category=category_filter or "", q=search_query, sort_by=sort_by, sort_order=sort_order))


@admin_bp.route("/talents/<int:talent_id>/edit", methods=["GET", "POST"])
@admin_required
def edit_talent(talent_id: int):
    status_filter = request.args.get("status", "en_attente")[:50]
    category_filter = request.args.get("category", "").strip()[:100] or None
    search_query = request.args.get("q", "").strip()[:100]
    sort_by = request.args.get("sort_by", "date_updated")[:50]
    sort_order = request.args.get("sort_order", "desc")[:10]

    form = TalentAdminForm()
    form.category.choices = get_talent_category_choices()
    form.status.choices = get_talent_status_choices()

    try:
        row = get_talent_by_id(talent_id)
    except DatabaseError:
        flash("Erreur lors de la récupération du talent.", "error")
        return redirect(url_for("admin.talents", status=status_filter, category=category_filter or "", q=search_query, sort_by=sort_by, sort_order=sort_order))

    if not row:
        flash("Talent introuvable.", "error")
        return redirect(url_for("admin.talents", status=status_filter, category=category_filter or "", q=search_query, sort_by=sort_by, sort_order=sort_order))

    talent = dict(row)

    form.category.choices = get_talent_category_choices(talent.get("category"))
    form.status.choices = get_talent_status_choices()

    if request.method == "GET":
        form.pseudo.data = talent["pseudo"]
        form.instagram.data = talent["instagram"]
        form.description.data = talent["description"]
        form.category.data = talent["category"] or ""
        form.image.data = talent["image"] or ""
        form.status.data = talent["status"]
        form.display_order.data = talent.get("display_order", 0) or 0

    if form.validate_on_submit():
        try:
            success, message = update_talent_full(
                talent_id=talent_id,
                pseudo=form.pseudo.data,
                instagram=form.instagram.data,
                description=form.description.data,
                category=form.category.data or "",
                image=form.image.data or "",
                status=form.status.data,
                display_order=form.display_order.data or 0,
            )
            if success:
                current_app.logger.info(
                    "Mise à jour admin du talent #%s par '%s' (%s)",
                    talent_id,
                    session.get("admin_username") or "inconnu",
                    request.remote_addr or "IP inconnue",
                )
                flash(message, "success")
                return redirect(
                    url_for("admin.talents", status=status_filter, category=category_filter or "", q=search_query, sort_by=sort_by, sort_order=sort_order)
                )
            else:
                flash(message, "warning")
        except DatabaseError:
            flash("Erreur lors de la mise à jour du talent.", "error")

    return render_template(
        "admin/edit_talent.html",
        form=form,
        admin_username=session.get("admin_username"),
        form_action=url_for(
            "admin.edit_talent",
            talent_id=talent_id,
            status=status_filter,
            category=category_filter or "",
            q=search_query,
            sort_by=sort_by,
            sort_order=sort_order,
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
    form = TalentAdminForm()
    form.category.choices = get_talent_category_choices()
    form.status.choices = get_talent_status_choices()

    if form.validate_on_submit():
        try:
            success, message = create_talent_admin(
                pseudo=form.pseudo.data,
                instagram=form.instagram.data,
                description=form.description.data,
                category=form.category.data or "",
                image=form.image.data or "",
                status=form.status.data,
                display_order=form.display_order.data or 0,
            )
            if success:
                current_app.logger.info(
                    "Création admin d'un talent (%s) par '%s' (%s)",
                    form.pseudo.data,
                    session.get("admin_username") or "inconnu",
                    request.remote_addr or "IP inconnue",
                )
                flash(message, "success")
                target_status = (
                    form.status.data if form.status.data in TALENT_STATUSES else "en_attente"
                )
                return redirect(url_for("admin.talents", status=target_status))
            else:
                flash(message, "error")
        except DatabaseError:
            flash("Erreur lors de l'ajout du talent.", "error")

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
