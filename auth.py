import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from .db import find_one, insert_one

from bson.objectid import ObjectId

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif find_one('user', condition={"username": username}) is not None:
            error = 'User {} is already registered.'.format(username)

        if error is None:
            password_hash = generate_password_hash(password)
            insert_one('user', document={"username": username, "password_hash": password_hash})
            return redirect(url_for('auth.login'))

        flash(error)

    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None
        user = find_one('user', condition={"username": username})

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password_hash'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = str(user['_id'])
            if 'source-login' in request.form:
                return redirect(url_for('event.source', sourceId=0))
            if 'user-login' in request.form:
                return redirect(url_for('user_events.user_events'))

        flash(error)

    return render_template('auth/login.html')

@bp.before_app_request
def load_logged_in_user():
    user_id = ObjectId(session.get('user_id'))

    if user_id is None:
        g.user = None
    else:
        g.user = find_one('user', condition={'_id': user_id})

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view
