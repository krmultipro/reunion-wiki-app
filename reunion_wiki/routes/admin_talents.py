# -*- coding: utf-8 -*-

from flask import Blueprint, abort, flash, redirect, render_template, request, session, url_for

from ..auth import admin_required
from ..forms.talent_forms import TalentActionForm, TalentForm
from ..services import talent_service
from ..services.talent_service import STATUSES
from ..utils import parse_positive_int


admin_talents_bp = Blueprint("admin_talents", __name__)


def _form_to_data(form):
    """Extrait les valeurs métier d'un TalentForm validé.

    Args:
        form (TalentForm): Formulaire validé.

    Returns:
        dict:
            Données prêtes pour talent_service.save_talent.
    """

    return {
        "name": form.name.data,
        "slug": form.slug.data,
        "category": form.category.data,
        "city": form.city.data,
        "description": form.description.data,
        "bio": form.bio.data,
        "instagram_url": form.instagram_url.data,
        "youtube_url": form.youtube_url.data,
        "tiktok_url": form.tiktok_url.data,
        "facebook_url": form.facebook_url.data,
        "website_url": form.website_url.data,
        "status": form.status.data,
        "display_order": form.display_order.data,
    }


def _populate_form(form, talent):
    """Préremplit le formulaire avec les données d'un talent.

    Args:
        form (TalentForm): Formulaire à remplir.
        talent (sqlite3.Row): Talent existant.

    Returns:
        None
    """

    form.name.data = talent["name"]
    form.slug.data = talent["slug"]
    form.category.data = talent["category"]
    form.city.data = talent["city"]
    form.description.data = talent["description"]
    form.bio.data = talent["bio"]
    form.instagram_url.data = talent["instagram_url"]
    form.youtube_url.data = talent["youtube_url"]
    form.tiktok_url.data = talent["tiktok_url"]
    form.facebook_url.data = talent["facebook_url"]
    form.website_url.data = talent["website_url"]
    form.status.data = talent["status"]
    form.display_order.data = talent["display_order"]


def _validate_action_form(talent_id):
    """Valide le formulaire CSRF d'une action talent.

    Args:
        talent_id (int): Identifiant attendu dans l'URL.

    Returns:
        bool:
            True si le formulaire est valide.
    """

    form = TalentActionForm()
    if not form.validate_on_submit():
        flash("Formulaire invalide.", "error")
        return False
    try:
        if int(form.talent_id.data) != talent_id:
            abort(400)
    except (TypeError, ValueError):
        abort(400)
    return True


@admin_talents_bp.route("/admin/talents", methods=["GET"])
@admin_required
def list_talents():
    status = (request.args.get("status") or "").strip() or None
    category = (request.args.get("category") or "").strip() or None
    query_text = (request.args.get("q") or "").strip()
    sort = (request.args.get("sort") or "recent").strip()
    page = parse_positive_int(request.args.get("page"), default=1)

    result = talent_service.get_admin_list(
        status=status,
        category=category,
        q=query_text,
        sort=sort,
        page=page,
    )
    action_forms = {item["id"]: TalentActionForm(talent_id=str(item["id"])) for item in result["items"]}

    return render_template(
        "admin/talents/list.html",
        items=result["items"],
        action_forms=action_forms,
        statuses=STATUSES,
        status_filter=status or "",
        category_filter=category or "",
        query_text=query_text,
        sort_filter=sort,
        page=result["page"],
        total_pages=result["total_pages"],
        total=result["total"],
        admin_username=session.get("admin_username"),
    )


@admin_talents_bp.route("/admin/talents/new", methods=["GET", "POST"])
@admin_required
def new_talent():
    form = TalentForm()
    if form.validate_on_submit():
        talent_id, errors = talent_service.save_talent(
            _form_to_data(form), image_file=form.image.data
        )
        if errors:
            for error in errors:
                flash(error, "error")
        else:
            flash("Talent créé.", "success")
            return redirect(url_for("admin_talents.edit_talent", talent_id=talent_id))

    return render_template(
        "admin/talents/form.html",
        form=form,
        current_image=None,
        form_action=url_for("admin_talents.new_talent"),
        page_title="Créer un talent",
        submit_label="Créer le talent",
        admin_username=session.get("admin_username"),
    )


@admin_talents_bp.route("/admin/talents/<int:talent_id>/edit", methods=["GET", "POST"])
@admin_required
def edit_talent(talent_id):
    talent = talent_service.get_talent(talent_id)
    if not talent:
        flash("Talent introuvable.", "error")
        return redirect(url_for("admin_talents.list_talents"))

    form = TalentForm()
    if request.method == "GET":
        _populate_form(form, talent)
    elif form.validate_on_submit():
        _talent_id, errors = talent_service.save_talent(
            _form_to_data(form), image_file=form.image.data, talent_id=talent_id
        )
        if errors:
            for error in errors:
                flash(error, "error")
        else:
            flash("Talent mis à jour.", "success")
            return redirect(url_for("admin_talents.edit_talent", talent_id=talent_id))

    return render_template(
        "admin/talents/form.html",
        form=form,
        current_image=talent["image"],
        talent_id=talent_id,
        form_action=url_for("admin_talents.edit_talent", talent_id=talent_id),
        page_title=f"Éditer « {talent['name']} »",
        submit_label="Enregistrer les modifications",
        admin_username=session.get("admin_username"),
    )


@admin_talents_bp.route("/admin/talents/<int:talent_id>/publish", methods=["POST"])
@admin_required
def publish_talent(talent_id):
    if not _validate_action_form(talent_id):
        return redirect(url_for("admin_talents.list_talents"))

    ok, errors = talent_service.publish(talent_id)
    if ok:
        flash("Talent publié.", "success")
    else:
        for error in errors:
            flash(error, "error")
    return redirect(request.referrer or url_for("admin_talents.list_talents"))


@admin_talents_bp.route("/admin/talents/<int:talent_id>/archive", methods=["POST"])
@admin_required
def archive_talent(talent_id):
    if not _validate_action_form(talent_id):
        return redirect(url_for("admin_talents.list_talents"))

    if talent_service.archive(talent_id):
        flash("Talent archivé.", "success")
    else:
        flash("Talent introuvable.", "error")
    return redirect(request.referrer or url_for("admin_talents.list_talents"))


@admin_talents_bp.route("/admin/talents/<int:talent_id>/delete", methods=["POST"])
@admin_required
def delete_talent(talent_id):
    if not _validate_action_form(talent_id):
        return redirect(url_for("admin_talents.list_talents"))

    if talent_service.delete_talent(talent_id):
        flash("Talent supprimé.", "success")
    else:
        flash("Talent introuvable.", "error")
    return redirect(url_for("admin_talents.list_talents"))
