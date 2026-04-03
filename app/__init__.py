from flask import Flask, render_template, send_from_directory
from .config import Config
from app.client.routes import api_blueprint


def create_app():
    from app.rag_agent.clinical_tool.utils import reset_clinical_trials_storage

    reset_clinical_trials_storage()
    app = Flask(__name__)
    app.config.from_object(Config)

    # Register the API blueprint
    app.register_blueprint(api_blueprint)

    @app.route('/')
    def home():
        return render_template("index.html")

    @app.route('/about')
    def about():
        return render_template("about.html")

    @app.route('/images/<path:filename>')
    def images(filename):
        return send_from_directory(Config.BASE_DIR / "images", filename)

    return app
