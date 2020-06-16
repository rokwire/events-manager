
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app, jsonify
)
from .config import Config

bp = Blueprint('home', __name__, url_prefix=Config.URL_PREFIX)

@bp.route('/', methods=['GET'])
def home():
    if 'error' in request.args:
        error = request.args['error']
        return render_template("home/home.html", error=error)
    else:
        return render_template("home/home.html")
