import os

from flask import Flask, current_app

from .config import Config
from .db import init_db

from .auth import bp as auth_bp

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    init_db(app)

    app.register_blueprint(auth_bp)

    return app
