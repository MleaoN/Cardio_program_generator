from flask import Flask
import os

def create_app():
    app = Flask(__name__)

    # MUST set secret key before using session
    app.secret_key = os.environ.get("SECRET_KEY", "super_secret_fallback_key")

    # Import and register routes blueprint
    from .routes import bp as routes_bp
    app.register_blueprint(routes_bp)

    return app
