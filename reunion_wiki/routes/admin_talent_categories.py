# -*- coding: utf-8 -*-
"""Routes d'administration des catégories de créateurs."""

from flask import Blueprint, abort, flash, redirect, render_template, request, session, url_for

from ..auth import admin_required
from ..forms.talent_category_forms import TalentCategoryActionForm, TalentCategoryForm
from ..services import talent_category_service


admin_talent_categories_bp = Blueprint("admin_talent_categories", __name__)


def _form_to_data(form):
    """Extrait les données utiles d'un formulaire de catégorie créateur.

    Args:
        form (TalentCategoryForm): Formulaire validé.

    Returns:
        dict:
            Données prêtes pour le service.
    """

    return {
        "name": form.name.data,
        "slug": form.slug.data,
    }


def _populate_form(form, category):
    """Préremplit un formulaire avec une catégorie existante.

    Args:
        form (TalentCategoryForm): Formulaire à remplir.
        category (sqlite3.Row): Catégorie existante.

    Returns:
        None
    """

    form.name.data = category["name"]
    form.slug.data = category["slug"]


def _validate_action_form(category_id):
    """Valide le formulaire CSRF d'une action catégorie créateur.

    Args:
        category_id (int): Identifiant attendu dans l'URL.

    Returns:
        bool:
            True si le formulaire est valide.
    """

    form = TalentCategoryActionForm()
    if not form.validate_on_submit():
        flash("Formulaire invalide.", "error")
        return False
    try:
        if int(form.category_id.data) != category_id:
            abort(400)
    except (TypeError, ValueError):
        abort(400)
    return True


@admin_talent_categories_bp.route("/admin/talent-categories", methods=["GET"])
@admin_required
def list_categories():
    categories = talent_category_service.list_categories()
    delete_forms = {
        category["id"]: TalentCategoryActionForm(category_id=str(category["id"]))
        for category in categories
    }
    return render_template(
        "admin/talent_categories/list.html",
        categories_=categories,
        delete_forms=delete_forms,
        admin_username=session.get("admin_username"),
    )


@admin_talent_categories_bp.route("/admin/talent-categories/new", methods=["GET", "POST"])
@admin_required
def new_category():
    form = TalentCategoryForm()
    if form.validate_on_submit():
        category_id, errors = talent_category_service.save_category(_form_to_data(form))
        if errors:
            for error in errors:
                flash(error, "error")
        else:
            flash("Catégorie créateur créée.", "success")
            return redirect(url_for("admin_talent_categories.edit_category", category_id=category_id))

    return render_template(
        "admin/talent_categories/form.html",
        form=form,
        form_action=url_for("admin_talent_categories.new_category"),
        page_title="Créer une catégorie créateur",
        submit_label="Créer la catégorie",
        admin_username=session.get("admin_username"),
    )


@admin_talent_categories_bp.route("/admin/talent-categories/<int:category_id>/edit", methods=["GET", "POST"])
@admin_required
def edit_category(category_id):
    category = talent_category_service.get_category(category_id)
    if not category:
        flash("Catégorie créateur introuvable.", "error")
        return redirect(url_for("admin_talent_categories.list_categories"))

    form = TalentCategoryForm()
    if request.method == "GET":
        _populate_form(form, category)
    elif form.validate_on_submit():
        _category_id, errors = talent_category_service.save_category(
            _form_to_data(form), category_id=category_id
        )
        if errors:
            for error in errors:
                flash(error, "error")
        else:
            flash("Catégorie créateur mise à jour.", "success")
            return redirect(url_for("admin_talent_categories.list_categories"))

    return render_template(
        "admin/talent_categories/form.html",
        form=form,
        form_action=url_for("admin_talent_categories.edit_category", category_id=category_id),
        page_title=f"Éditer la catégorie créateur « {category['name']} »",
        submit_label="Enregistrer",
        admin_username=session.get("admin_username"),
    )


@admin_talent_categories_bp.route("/admin/talent-categories/<int:category_id>/delete", methods=["POST"])
@admin_required
def delete_category(category_id):
    if not _validate_action_form(category_id):
        return redirect(url_for("admin_talent_categories.list_categories"))

    ok, errors = talent_category_service.delete_category(category_id)
    if ok:
        flash("Catégorie créateur supprimée.", "success")
    else:
        for error in errors:
            flash(error, "error")
    return redirect(url_for("admin_talent_categories.list_categories"))
