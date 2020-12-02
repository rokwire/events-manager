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
    gitinfo = "{}#branch:{} sha:{}".format(repo.tags[-1], repo.active_branch.name, repo.head.commit.hexsha[0: 6])
    if 'error' in request.args:
        error = request.args['error']
        return render_template("home/home.html", error=error, gitinfo=gitinfo)
    else:
        return render_template("home/home.html", gitinfo=gitinfo)
