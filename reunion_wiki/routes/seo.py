from flask import Blueprint, current_app, make_response, send_from_directory


seo_bp = Blueprint("seo", __name__)


@seo_bp.route('/service-worker.js')
def service_worker():
    response = make_response(send_from_directory(current_app.static_folder, 'service-worker.js'))
    response.headers['Content-Type'] = 'application/javascript'
    return response    


@seo_bp.route('/google87e16279463c4021.html')
def google_verification():
    return current_app.send_static_file('google87e16279463c4021.html')


@seo_bp.route('/robots.txt')
def robots_txt():
    return send_from_directory(current_app.static_folder, 'robots.txt')

@seo_bp.route('/sitemap.xml')
def sitemap():
    return send_from_directory(current_app.static_folder, 'sitemap.xml')
