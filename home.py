
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app, jsonify
)
from .config import Config
from git import Repo
import os

bp = Blueprint('home', __name__, url_prefix=Config.URL_PREFIX)

@bp.route('/', methods=['GET'])
def home():
    repo = Repo(os.path.dirname(os.path.realpath(__file__)))
    gitinfo = "{}#branch:{} sha:{}".format(Config.VERSION, repo.active_branch.name, repo.head.commit.hexsha[0: 6])
    if 'error' in request.args:
        error = request.args['error']
        return render_template("home/home.html", error=error, gitinfo=gitinfo)
    else:
        return render_template("home/home.html", gitinfo=gitinfo)
