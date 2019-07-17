import os
import atexit

from flask import Flask, current_app, redirect, url_for, Blueprint

from .config import Config
from .db import init_db

from .auth import bp as auth_bp
from .event import bp as event_bp
from .user_events import userbp as user_bp
from .scheduler import create_scheduler, drop_scheduler

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    init_db(app)

    try:
        os.mkdir(app.config['WEBTOOL_IMAGE_MOUNT_POINT'])
    except OSError:
        pass

    app.register_blueprint(auth_bp)
    # app.register_blueprint(user_bp)
    app.register_blueprint(event_bp)

    app.scheduler = create_scheduler(app)
    app.scheduler.start()
    atexit.register(drop_scheduler, scheduler=app.scheduler)

    @app.route('/')
    def index():
        return redirect(url_for('auth.login'))

    return app
