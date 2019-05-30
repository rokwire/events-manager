import os

from flask import Flask, current_app

from .config import Config
from .db import init_db

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)
    
    init_db(app)
    
    return app

