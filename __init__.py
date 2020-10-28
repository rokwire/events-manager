#  Copyright 2020 Board of Trustees of the University of Illinois.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import os
import atexit

from flask import Flask, current_app, redirect, url_for, Blueprint, session

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

    return app
