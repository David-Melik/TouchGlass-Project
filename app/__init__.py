from flask import Flask
from .models import db
from .views import register_views
from .bac_views import bac_views  # type: ignore # Importer le nouveau blueprint pour le BAC


def create_app():
    app = Flask(__name__)
    app.config.from_object("app.config.Config")

    # Initialiser la base de données
    db.init_app(app)

    # Enregistrer les blueprints existants
    app.register_blueprint(register_views)

    # Enregistrer le blueprint pour le calcul du BAC
    app.register_blueprint(bac_views)

    return app
