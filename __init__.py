import os

from flask import Flask, current_app, redirect, url_for, Blueprint

from .config import Config
from .db import init_db

from .auth import bp as auth_bp
from .event import bp as event_bp
from .user_events import userbp as user_bp

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    init_db(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(event_bp)

    @app.route('/')
    def index():
        return redirect(url_for('auth.login'))

    return app
