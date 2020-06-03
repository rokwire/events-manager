import os
import atexit

from flask import Flask, current_app, redirect, url_for, Blueprint, session, render_template

from .config import Config
from .db import init_db

from .auth import check_login
from .auth import bp as auth_bp
from .event import bp as event_bp
from .home import bp as home_bp
from .user_events import userbp as user_bp
from .scheduler import create_scheduler, drop_scheduler
from .utilities import source_utilities

def create_app(config_class=Config):
    if Config is not None and Config.URL_PREFIX is not None:
        prefix = Config.URL_PREFIX
        staticpath = prefix+'/static'
    else:
        prefix = None
        staticpath = '/static'
    app = Flask(__name__, static_url_path=staticpath)
    app.config.from_object(Config)

    init_db(app)

    try:
        os.mkdir(app.config['WEBTOOL_IMAGE_MOUNT_POINT'])
    except OSError:
        pass

    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(event_bp)
    app.register_blueprint(home_bp)

    app.scheduler = create_scheduler(app)
    app.scheduler.start()
    atexit.register(drop_scheduler, scheduler=app.scheduler)

    with app.app_context():
        source_utilities.load_calendar_into_db()

    @app.route('/')
    @check_login
    def index():
        return redirect(url_for('home.home'))

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(e):
        return render_template('errors/500.html'), 500

    return app
