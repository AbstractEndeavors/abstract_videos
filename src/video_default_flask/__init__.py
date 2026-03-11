from .routes import (
    #image_routes_bp,
    #video_routes_bp,
   # repo_routes_bp,
   # pdf_routes_bp,
    service_calls_bp,
   # ocr_routes_bp,
   # audio_routes_bp,
   # text_routes_bp
    #call_routes_bp
    )
from flask import Flask
from flask_cors import CORS
#call_routes = [call_routes_bp,video_routes_bp,info_routes_bp]
def media_app():
    """Flask app factory with fully relaxed security settings."""
    app = Flask(
        __name__,
        static_folder='static',
        static_url_path='/static',
        template_folder='templates'
    )
    
    # Register Blueprints
    #for route in call_routes:
    #    app.register_blueprint(route)
    app.register_blueprint(service_calls_bp)
    #app.register_blueprint(video_routes_bp)
    #app.register_blueprint(info_routes_bp)

    # Relax CORS for all routes: Allow all origins
    CORS(app, resources={r"/*": {"origins": "*"}})
    
    @app.after_request
    def relax_security_headers(response):
        # Relax Content Security Policy to allow all sources and inline scripts/styles
        response.headers["Content-Security-Policy"] = "default-src * 'unsafe-inline' 'unsafe-eval';"
        # Allow all CORS headers and methods
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS, PUT, DELETE"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With"
        return response

    return app
