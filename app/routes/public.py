"""Public-facing routes (home, categories, forms, etc.)."""

from __future__ import annotations

from datetime import datetime

from flask import (
    Blueprint,
    current_app,
    flash,
    make_response,
    redirect,
    render_template,
    request,
    send_from_directory,
    url_for,
)

from ..database import DatabaseError
from ..extensions import limiter
from ..forms import SiteForm, TalentProposalForm
from ..services.emails import send_submission_notification
from ..services.sites import (
    get_all_validated_sites,
    get_categories,
    get_categories_slug,
    get_derniers_sites_global,
    get_nom_categorie_depuis_slug,
    get_sites_by_category,
    get_sites_en_vedette,
    search_sites,
    submit_site_proposal,
)
from ..services.talents import create_talent_proposal, get_talents_data
from ..utils.text import slugify

public_bp = Blueprint("public", __name__)


@public_bp.route("/", methods=["GET", "POST"])
@limiter.limit(lambda: "1000 per hour" if current_app.config.get("DEBUG") else "5 per hour")
def accueil():
    data = get_sites_en_vedette()
    derniers_sites = get_derniers_sites_global(12)
    talents_home = get_talents_data()

    form_inline = SiteForm()
    form_inline.categorie.choices = [(cat, cat) for cat in get_categories()]
    form_inline.categorie.choices.insert(0, ("", "Sélectionnez une catégorie"))

    # Formulaire pour les talents
    form_talent = TalentProposalForm()
    if form_talent.validate_on_submit():
        # Log pour détection d'abus et monitoring
        current_app.logger.info(
            f"Proposition talent (accueil): '{form_talent.pseudo.data}' depuis IP: {request.remote_addr or 'inconnue'}"
        )
        
        success = create_talent_proposal(
            form_talent.pseudo.data,
            form_talent.instagram.data,
            form_talent.description.data,
            form_talent.category.data or None,
        )
        if success:
            flash(
                "Merci ! Ta proposition de talent est en attente de validation.",
                "success",
            )
            return redirect(url_for("public.accueil") + "#talents-tab")
        flash(
            "Erreur lors de l'enregistrement de ta proposition. Réessaie plus tard.",
            "error",
        )

    return render_template(
        "index.html",
        data=data,
        derniers_sites=derniers_sites,
        talents=talents_home,
        form_inline=form_inline,
        form_talent=form_talent,
    )


@public_bp.route("/categorie/<slug>")
def voir_categorie(slug: str):
    # Limite de longueur du slug pour éviter les abus
    slug = slug[:100]
    nom_categorie = get_nom_categorie_depuis_slug(slug)
    if not nom_categorie:
        return render_template("404.html"), 404

    canonical_slug = slugify(nom_categorie)
    if slug != canonical_slug:
        return redirect(url_for("public.voir_categorie", slug=canonical_slug), code=301)

    try:
        sites = get_sites_by_category(nom_categorie)
    except DatabaseError:
        return render_template("500.html"), 500

    seo_title = f"{nom_categorie} à La Réunion – Réunion Wiki"
    seo_description = (
        f"Découvrez les meilleurs sites {nom_categorie.lower()} : infos utiles et adresses à La Réunion."
    )
    canonical = url_for("public.voir_categorie", slug=canonical_slug, _external=True)

    form_inline = SiteForm()
    categories = get_categories()
    form_inline.categorie.choices = [(cat, cat) for cat in categories]
    form_inline.categorie.choices.insert(0, ("", "Sélectionnez une catégorie"))
    if nom_categorie in categories:
        form_inline.categorie.data = nom_categorie

    return render_template(
        "categorie.html",
        nom_categorie=nom_categorie,
        sites=sites,
        slug=canonical_slug,
        seo_title=seo_title,
        seo_description=seo_description,
        canonical=canonical,
        form_inline=form_inline,
    )


@public_bp.route("/nouveaux-sites")
@limiter.limit(lambda: "1000 per hour" if current_app.config.get("DEBUG") else "60 per minute")
def nouveaux_sites():
    try:
        sites = get_all_validated_sites()
    except DatabaseError:
        return render_template("500.html"), 500

    return render_template("nouveaux_sites.html", sites=sites)


@public_bp.route("/recherche")
@limiter.limit(lambda: "1000 per hour" if current_app.config.get("DEBUG") else "30 per minute")
def search():
    # Limite de longueur pour éviter les abus (max 100 caractères)
    query = request.args.get("q", "").strip()[:100]
    results = []
    total = 0

    if query and len(query) >= 2:
        # Log pour détecter les patterns d'abus et améliorer la sécurité
        current_app.logger.info(
            f"Recherche: '{query[:50]}' depuis IP: {request.remote_addr or 'inconnue'}"
        )
        
        try:
            # Limite réduite à 30 résultats pour optimiser les performances
            results = search_sites(query, limit=30)
            total = len(results)
        except DatabaseError:
            flash(
                "Impossible d'accéder à la base de données pour la recherche.",
                "error",
            )
            results = []
            total = 0
    elif query:
        flash("Tape au moins 2 caractères pour lancer la recherche.", "error")

    return render_template(
        "search.html",
        query=query,
        results=results,
        total=total,
    )


@public_bp.route("/blog")
def blog():
    categories = get_categories()
    categories_slug = get_categories_slug()
    return render_template(
        "blog.html", categories=categories, categories_slug=categories_slug
    )


@public_bp.route("/talents", methods=["GET", "POST"])
@limiter.limit(lambda: "1000 per hour" if current_app.config.get("DEBUG") else "5 per hour")
def talents():
    form = TalentProposalForm()
    if form.validate_on_submit():
        # Log pour détection d'abus et monitoring
        current_app.logger.info(
            f"Proposition talent (page talents): '{form.pseudo.data}' depuis IP: {request.remote_addr or 'inconnue'}"
        )
        
        success = create_talent_proposal(
            form.pseudo.data,
            form.instagram.data,
            form.description.data,
            form.category.data or None,
        )
        if success:
            flash(
                "Merci ! Ta proposition de talent est en attente de validation.",
                "success",
            )
            return redirect(url_for("public.talents"))
        flash(
            "Erreur lors de l'enregistrement de ta proposition. Réessaie plus tard.",
            "error",
        )
    talents_by_category = get_talents_data()
    return render_template("talents.html", talents=talents_by_category, form=form)


@public_bp.route("/proposer-talent", methods=["GET", "POST"])
@limiter.limit(lambda: "1000 per hour" if current_app.config.get("DEBUG") else "5 per hour")
def proposer_talent():
    """Page dédiée pour proposer un talent avec catégorie pré-remplie."""
    form = TalentProposalForm()
    
    # Récupérer la catégorie depuis la query string avec limite de longueur
    category_param = request.args.get("category", "").strip()[:50]
    if category_param:
        form.category.data = category_param
    
    if form.validate_on_submit():
        # Log pour détection d'abus et monitoring
        current_app.logger.info(
            f"Proposition talent: '{form.pseudo.data}' depuis IP: {request.remote_addr or 'inconnue'}"
        )
        
        success = create_talent_proposal(
            form.pseudo.data,
            form.instagram.data,
            form.description.data,
            form.category.data or None,
        )
        if success:
            flash(
                "Merci ! Ta proposition de talent est en attente de validation.",
                "success",
            )
            return redirect(url_for("public.talents"))
        flash(
            "Erreur lors de l'enregistrement de ta proposition. Réessaie plus tard.",
            "error",
        )
    
    return render_template("proposer_talent.html", form=form, category=category_param)


@public_bp.route("/mentions-legales")
def mentions_legales():
    return render_template("mentions_legales.html")


@public_bp.route("/contact")
def contact():
    contact_channels = [
        {
            "title": "Email",
            "value": "reunionwiki974@gmail.com",
            "action": "mailto:reunionwiki974@gmail.com",
            "label": "Envoyer un email",
        },
        {
            "title": "Formulaire",
            "value": "Formulaire Google",
            "action": "https://forms.gle/GScJkMiEZXVSted78",
            "label": "Proposer une idée",
        },
        {
            "title": "Instagram",
            "value": "@kery.rdd",
            "action": "https://www.instagram.com/kery.rdd",
            "label": "Suivre le projet",
        },
    ]

    support_blocks = [
        {
            "title": "Besoin d'aide rapide ?",
            "description": "Consulte la FAQ.",
            "link": url_for("public.faq"),
            "label": "Voir la FAQ",
        },
        {
            "title": "Tu veux contribuer ?",
            "description": "Propose un site directement via le formulaire dédié ou contacte moi pour des données supplémentaires.",
            "link": url_for("public.formulaire"),
            "label": "Proposer un site",
        },
    ]

    return render_template(
        "contact.html",
        contact_channels=contact_channels,
        support_blocks=support_blocks,
    )


@public_bp.route("/service-worker.js")
def service_worker():
    response = make_response(send_from_directory("static", "service-worker.js"))
    response.headers["Content-Type"] = "application/javascript"
    return response


@public_bp.route("/google87e16279463c4021.html")
def google_verification():
    return current_app.send_static_file("google87e16279463c4021.html")


@public_bp.route("/formulaire", methods=["GET", "POST"])
@limiter.limit(lambda: "100 per minute" if current_app.config.get("DEBUG") else "5 per minute")
def formulaire():
    form = SiteForm()
    form.categorie.choices = [(cat, cat) for cat in get_categories()]
    form.categorie.choices.insert(0, ("", "Sélectionnez une catégorie"))

    if form.validate_on_submit():
        # Log pour détection d'abus et monitoring
        current_app.logger.info(
            f"Proposition site: '{form.nom.data}' ({form.lien.data}) "
            f"depuis IP: {request.remote_addr or 'inconnue'}"
        )
        
        success, message = submit_site_proposal(
            nom=form.nom.data,
            lien=form.lien.data,
            description=form.description.data,
            categorie=form.categorie.data,
            ville=form.ville.data or None,
        )
        
        if success:
            # Envoi notification email (non bloquant)
            try:
                send_submission_notification(
                    {
                        "nom": form.nom.data,
                        "ville": form.ville.data,
                        "lien": form.lien.data,
                        "description": form.description.data,
                        "categorie": form.categorie.data,
                        "date_submission": datetime.utcnow().strftime("%d/%m/%Y %H:%M"),
                        "remote_addr": request.remote_addr or "IP inconnue",
                    }
                )
            except Exception as e:
                # Log l'erreur mais ne bloque pas l'utilisateur
                current_app.logger.error(f"Erreur envoi notification email: {e}")
            
            flash(message, "success")
            return redirect(url_for("public.accueil"))
        else:
            flash(message, "error")

    return render_template("formulaire.html", form=form)


@public_bp.route("/faq")
def faq():
    return render_template("faq.html")
