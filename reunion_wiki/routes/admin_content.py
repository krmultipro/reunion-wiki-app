# -*- coding: utf-8 -*-

from flask import Blueprint, abort, flash, redirect, render_template, request, session, url_for

from ..auth import admin_required
from ..forms.content_forms import ContentDeleteForm, ContentForm
from ..services import content_service
from ..services.content_service import CONTENT_TYPES, STATUSES
from ..utils import parse_positive_int


admin_content_bp = Blueprint("admin_content", __name__)


def _form_to_data(form):
    """Extrait les valeurs métier d'un ContentForm validé.

    Args:
        form (ContentForm): Formulaire validé.

    Returns:
        dict: Données prêtes pour content_service.save_content.
    """

    return {
        "content_type": form.content_type.data,
        "title": form.title.data,
        "slug": form.slug.data,
        "summary": form.summary.data,
        "body": form.body.data,
        "meta_title": form.meta_title.data,
        "meta_description": form.meta_description.data,
        "status": form.status.data,
        "remove_featured_image": form.remove_featured_image.data,
    }


@admin_content_bp.route("/admin/content", methods=["GET"])
@admin_required
def list_content():
    content_type = (request.args.get("type") or "").strip() or None
    status = (request.args.get("status") or "").strip() or None
    query_text = (request.args.get("q") or "").strip()
    sort = (request.args.get("sort") or "recent").strip()
    page = parse_positive_int(request.args.get("page"), default=1)

    result = content_service.get_admin_list(
        content_type=content_type, status=status, q=query_text, sort=sort, page=page
    )

    delete_forms = {item["id"]: ContentDeleteForm(content_id=str(item["id"])) for item in result["items"]}

    return render_template(
        "admin/content/list.html",
        items=result["items"],
        delete_forms=delete_forms,
        content_types=CONTENT_TYPES,
        statuses=STATUSES,
        type_filter=content_type or "",
        status_filter=status or "",
        query_text=query_text,
        sort_filter=sort,
        page=result["page"],
        total_pages=result["total_pages"],
        total=result["total"],
        admin_username=session.get("admin_username"),
    )


@admin_content_bp.route("/admin/content/new", methods=["GET", "POST"])
@admin_required
def new_content():
    form = ContentForm()
    if form.validate_on_submit():
        content_id, errors = content_service.save_content(
            _form_to_data(form), image_file=form.featured_image.data
        )
        if errors:
            for error in errors:
                flash(error, "error")
        else:
            flash("Contenu créé.", "success")
            return redirect(url_for("admin_content.edit_content", content_id=content_id))

    return render_template(
        "admin/content/form.html",
        form=form,
        featured_image=None,
        form_action=url_for("admin_content.new_content"),
        page_title="Créer un contenu",
        submit_label="Créer le contenu",
        admin_username=session.get("admin_username"),
    )


@admin_content_bp.route("/admin/content/<int:content_id>/edit", methods=["GET", "POST"])
@admin_required
def edit_content(content_id):
    from ..repositories import content_repository

    row = content_repository.get_by_id(content_id)
    if not row:
        flash("Contenu introuvable.", "error")
        return redirect(url_for("admin_content.list_content"))

    form = ContentForm()

    if request.method == "GET":
        form.content_type.data = row["content_type"]
        form.title.data = row["title"]
        form.slug.data = row["slug"]
        form.summary.data = row["summary"]
        form.body.data = row["body"]
        form.meta_title.data = row["meta_title"]
        form.meta_description.data = row["meta_description"]
        form.status.data = row["status"]
    elif form.validate_on_submit():
        _content_id, errors = content_service.save_content(
            _form_to_data(form), image_file=form.featured_image.data, content_id=content_id
        )
        if errors:
            for error in errors:
                flash(error, "error")
        else:
            flash("Contenu mis à jour.", "success")
            return redirect(url_for("admin_content.edit_content", content_id=content_id))

    return render_template(
        "admin/content/form.html",
        form=form,
        featured_image=row["featured_image"],
        content_id=content_id,
        public_slug=row["slug"] if row["status"] == "published" else None,
        form_action=url_for("admin_content.edit_content", content_id=content_id),
        page_title=f"Éditer « {row['title']} »",
        submit_label="Enregistrer les modifications",
        admin_username=session.get("admin_username"),
    )


def _validate_action_form(content_id):
    """Valide le formulaire CSRF d'une action et le rapproche de l'URL.

    Args:
        content_id (int): Identifiant attendu dans l'URL.

    Returns:
        None: Interrompt via abort/redirect en cas d'invalidité.
    """

    form = ContentDeleteForm()
    if not form.validate_on_submit():
        flash("Formulaire invalide.", "error")
        return False
    try:
        if int(form.content_id.data) != content_id:
            abort(400)
    except (TypeError, ValueError):
        abort(400)
    return True


@admin_content_bp.route("/admin/content/<int:content_id>/publish", methods=["POST"])
@admin_required
def publish_content(content_id):
    if not _validate_action_form(content_id):
        return redirect(url_for("admin_content.list_content"))

    ok, errors = content_service.publish(content_id)
    if ok:
        flash("Contenu publié.", "success")
    else:
        for error in errors:
            flash(error, "error")
    return redirect(request.referrer or url_for("admin_content.list_content"))


@admin_content_bp.route("/admin/content/<int:content_id>/unpublish", methods=["POST"])
@admin_required
def unpublish_content(content_id):
    if not _validate_action_form(content_id):
        return redirect(url_for("admin_content.list_content"))

    if content_service.unpublish(content_id):
        flash("Contenu repassé en brouillon.", "success")
    else:
        flash("Contenu introuvable.", "error")
    return redirect(request.referrer or url_for("admin_content.list_content"))


@admin_content_bp.route("/admin/content/<int:content_id>/archive", methods=["POST"])
@admin_required
def archive_content(content_id):
    if not _validate_action_form(content_id):
        return redirect(url_for("admin_content.list_content"))

    if content_service.archive(content_id):
        flash("Contenu archivé.", "success")
    else:
        flash("Contenu introuvable.", "error")
    return redirect(request.referrer or url_for("admin_content.list_content"))


@admin_content_bp.route("/admin/content/<int:content_id>/delete", methods=["POST"])
@admin_required
def delete_content(content_id):
    if not _validate_action_form(content_id):
        return redirect(url_for("admin_content.list_content"))

    if content_service.delete_content(content_id):
        flash("Contenu supprimé.", "success")
    else:
        flash("Contenu introuvable.", "error")
    return redirect(url_for("admin_content.list_content"))
