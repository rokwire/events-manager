import os

from flask import Flask, current_app
from flask_pymongo import PyMongo

from flaskr.config import Config

mongo = PyMongo()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    # init database connector
    if app.config['DBTYPE'] == 'mongoDB':
        mongo.init_app(app)
        app.config['DBCLIENT']=mongo
    else:
        pass

    from flaskr.auth import bp as auth_bp
    app.register_blueprint(auth_bp)


    return app