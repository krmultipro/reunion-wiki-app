from flask import Blueprint, Response, abort, current_app, make_response, request, send_from_directory, session, url_for

from ..services import sitemap_service
from ..repositories import media_repository


seo_bp = Blueprint("seo", __name__)


@seo_bp.route("/service-worker.js")
def service_worker():
    response = make_response(send_from_directory(current_app.static_folder, "service-worker.js"))
    response.headers["Content-Type"] = "application/javascript"
    return response


@seo_bp.route("/google87e16279463c4021.html")
def google_verification():
    return current_app.send_static_file("google87e16279463c4021.html")


@seo_bp.route("/robots.txt")
def robots_txt():
    if request.host.split(":")[0].lower() == "dev.reunionwiki.re":
        return Response("User-agent: *\nDisallow: /\n", mimetype="text/plain")
    return Response("User-agent: *\nDisallow: /admin\nDisallow: /proposition-confirmee/\n"
                    + "Sitemap: " + url_for("sitemap", _external=True) + "\n", mimetype="text/plain")


@seo_bp.route("/static/uploads/<path:filename>")
def uploaded_file(filename):
    """Sert les fichiers uploadés depuis le dossier persistant configuré."""
    if not session.get("admin_authenticated") and not media_repository.is_published_media("uploads/" + filename):
        abort(404)
    return send_from_directory(current_app.config["UPLOAD_FOLDER"], filename)


@seo_bp.route("/sitemap.xml")
def sitemap():
    """Sitemap généré dynamiquement : chaque contenu publié y apparaît."""
    xml = sitemap_service.build_sitemap_xml()
    return Response(xml, mimetype="application/xml")
