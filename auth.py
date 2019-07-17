import functools
import ldap

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from .db import find_one, insert_one

from bson.objectid import ObjectId

bp = Blueprint('auth', __name__, url_prefix='/auth')

def login_db(username, password, error):
    user = find_one('user', condition={"username": username})

    if not user:
        error = 'Incorrect username.'
    elif not check_password_hash(user['password_hash'], password):
        error = 'Incorrect password.'

    if error is None:
        session.clear()
        session['user_id'] = str(user['_id'])
        return True

    flash(error)
    return False

def login_ldap(username, password, error):
    ldap_hostname = current_app.config['LDAP_HOSTNAME']
    ldap_client = ldap.initialize(ldap_hostname)
    ldap_client.set_option(ldap.OPT_REFERRALS, 0)
    user_dn = "uid=%s,%s,%s" % (username, current_app.config['LDAP_USER_DN'], current_app.config['LDAP_BASE_DN'])
    group_dn = "%s,%s" % (current_app.config['LDAP_GROUP_DN'], current_app.config['LDAP_BASE_DN'])
    try:
        ldap_client.protocol_version = ldap.VERSION3
        ldap_client.simple_bind_s(user_dn, password)
    except Exception as ex:
        error = ex

    try:

        search_scope = ldap.SCOPE_SUBTREE
        search_filter = "(&(objectClass=%s)(memberOf=cn=%s,%s)(uid=%s))" % (current_app.config['LDAP_OBJECTCLASS'],
                                                                            current_app.config['LDAP_GROUP'],
                                                                            group_dn, username)
        ldap_result = ldap_client.search_s(current_app.config['LDAP_BASE_DN'], search_scope, search_filter)
        if 0 == len(ldap_result):
            error = "cannot find in this group"

    except Exception as ex:
        error = ex

    ldap_client.unbind_s()
    user = dict()
    admins = current_app.config['ADMINS']
    user['admin'] = False
    if username in admins:
        user['admin'] = True
    user['id'] = username
    if error is None:
        session.clear()
        session['user_id'] = user['id']
        session['admin'] = user['admin']
        return True

    flash(error)
    return False

# @bp.route('/register', methods=('GET', 'POST'))
# def register():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
#         error = None

#         if not username:
#             error = 'Username is required.'
#         elif not password:
#             error = 'Password is required.'
#         elif find_one('user', condition={"username": username}):
#             error = 'User {} is already registered.'.format(username)

#         if error is None:
#             password_hash = generate_password_hash(password)
#             insert_one('user', document={"username": username, "password_hash": password_hash})
#             return redirect(url_for('auth.login'))

#         flash(error)

#     return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None

        if current_app.config['LDAP_ON']: # log in using LDAP
            result = login_ldap(username, password, error)
        else:
            result = login_db(username, password, error)

        if result: # log in successful
            if 'source-login' in request.form:
                session['mode'] = 'source'
                return redirect(url_for('event.source', sourceId=0))
            if 'user-login' in request.form:
                session['mode'] = 'user'
                return redirect(url_for('user_events.user_events'))

        flash(error)

    if session.get('mode') == 'source':
        return redirect(url_for('event.source', sourceId=0))
    if session.get('mode') == 'user':
        return redirect(url_for('user_events.user_events'))
    return render_template('auth/login.html')

@bp.before_app_request
def load_logged_in_user_db():
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
