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

import functools
import ldap

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app
)
from werkzeug.security import check_password_hash, generate_password_hash

from .db import find_one, insert_one

from bson.objectid import ObjectId
from .config import Config

from oic.oic import Client
from oic.utils.authn.client import CLIENT_AUTHN_METHOD
from oic.oic.message import AuthorizationResponse, ClaimsRequest, Claims
from oic.oic.message import RegistrationResponse
from oic import rndstr
from oic.utils.http_util import Redirect

bp = Blueprint('auth', __name__, url_prefix=Config.URL_PREFIX+'/auth')
# current_app.config.from_pyfile('config.py', silent=True)
# Create OIDC client
client = Client(client_authn_method=CLIENT_AUTHN_METHOD)
# Get authentication provider details by hitting the issuer URL.
provider_info = client.provider_config(Config.ISSUER_URL)
# Store registration details
info = {"client_id": Config.CLIENT_ID, "client_secret": Config.CLIENT_SECRET, "redirect_uris": Config.REDIRECT_URIS}
client_reg = RegistrationResponse(**info)
client.store_registration_info(client_reg)

def check_login(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        access = session.get("access")
        if access is not None:
            if Config.ROLE.get(access) is not None:
                return redirect(Config.ROLE.get(access)[1])
        return view(**kwargs)
    return wrapped_view

def role_required(role):
    def decorator(view):
        @functools.wraps(view)
        def decorated_function(**kwargs):
            access = session.get("access")
            if access is None:
                return redirect(url_for("auth.login"))
            else:
                if Config.ROLE.get(access) is not None:
                    if Config.ROLE.get(access)[0] <= Config.ROLE.get(role)[0] and access != role:
                       return redirect(Config.ROLE.get(access)[1])
                else:
                    return redirect(url_for("auth.login"))
                return view(**kwargs)
        return decorated_function
    return decorator


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

def login_shi():
    # session["mode"] = "shibboleth"
    session["state"] = rndstr()
    session["nonce"] = rndstr()
    claims_request = ClaimsRequest(
        userinfo=Claims(
            uiucedu_uin={"essential": True}
        )
    )
    args = {
        "client_id": client.client_id,
        "response_type": "code",
        "scope": Config.SCOPES,
        "claims": claims_request,
        "nonce": session["nonce"],
        "redirect_uri": client.registration_response["redirect_uris"][0],
        "state": session["state"]
    }
    auth_req = client.construct_AuthorizationRequest(request_args=args)
    login_url = auth_req.request(client.authorization_endpoint)
    return Redirect(login_url)

    # if request.method == 'POST':
    #     username = request.form['username']
    #     password = request.form['password']
    #     error = None
    #
    #     if current_app.config['LDAP_ON']: # log in using LDAP
    #         result = login_ldap(username, password, error)
    #     else:
    #         result = login_db(username, password, error)
    #
    #     if result: # log in successful
    #         if 'source-login' in request.form:
    #             session['mode'] = 'source'
    #             return redirect(url_for('event.source', sourceId=0))
    #         if 'user-login' in request.form:
    #             session['mode'] = 'user'
    #             return redirect(url_for('user_events.user_events'))
    #
    #     flash(error)
    #
    # if session.get('mode') == 'source':
    #     return redirect(url_for('event.source', sourceId=0))
    # if session.get('mode') == 'user':
    #     return redirect(url_for('user_events.user_events'))
    # return render_template('auth/login.html')

# @bp.route('/register', methods=('GET', 'POST'))
# def register():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
#         error = None
#
#         if not username:
#             error = 'Username is required.'
#         elif not password:
#             error = 'Password is required.'
#         elif find_one('user', condition={"username": username}):
#             error = 'User {} is already registered.'.format(username)
#
#         if error is None:
#             password_hash = generate_password_hash(password)
#             insert_one('user', document={"username": username, "password_hash": password_hash})
#             return redirect(url_for('auth.login'))
#
#         flash(error)
#
#     return render_template('auth/register.html')


@bp.route('/login')
@check_login
def login():
    if Config.LOGIN_MODE == "shibboleth":
        return login_shi()

@bp.route('/callback')
def callback():
    if Config.LOGIN_MODE != "shibboleth":
        return redirect(url_for("auth.login"))
    response = request.environ["QUERY_STRING"]
    authentication_response = client.parse_response(AuthorizationResponse, info=response, sformat="urlencoded")
    code = authentication_response["code"]
    try:
        assert authentication_response["state"] == session["state"]
    except KeyError:
        return redirect(url_for("home.home", error="Unexpected Error, please try again"))
    args = {"code": code}
    token_response = client.do_access_token_request(state=authentication_response["state"],
                                                    request_args=args,
                                                    authn_method="client_secret_basic")
    user_info = client.do_user_info_request(state=authentication_response["state"])

    if "uiucedu_is_member_of" not in user_info.to_dict():
        session.clear()
        return redirect(url_for("home.home", error="You don't have permission to login the event manager"))
    rokwireAuth = list(filter(
        lambda x: "urn:mace:uiuc.edu:urbana:authman:app-rokwire-service-policy-" in x, 
        user_info.to_dict()["uiucedu_is_member_of"]
    ))
    if len(rokwireAuth) == 0:
        return redirect(url_for("auth.login"))
    else:
        # fill in user information
        session["name"] = user_info.to_dict()["name"]
        session["email"] = user_info.to_dict()["email"]
        # check for corresponding privilege
        isUserAdmin = False 
        isSourceAdmin = False
        for tag in rokwireAuth:
            if "rokwire em user events admins" in tag:
                isUserAdmin = True
            if "rokwire em calendar events admins" in tag:
                isSourceAdmin = True
        # TODO: we are storing cookie by our own but not by code, may change it later
        if isUserAdmin and isSourceAdmin:
            session["access"] = "both"
            session.permanent = True
            return redirect(url_for("auth.select_events"))
        elif isUserAdmin:
            session["access"] = "user"
            session.permanent = True
            return redirect(url_for("user_events.user_events"))
        elif isSourceAdmin:
            session["access"] = "source"
            session.permanent = True
            return redirect(url_for("event.source", sourceId=0))
        else:
            session.clear()
            return redirect(url_for("home.home", error="You don't have permission to login the event manager"))

    # if "member" in user_info.to_dict()["eduperson_affiliation"]:
    #     return redirect(url_for('user_events.user_events'))
    # else:
    #     return redirect(url_for('event.source', sourceId=0))
    # return user_info.to_json()

@bp.route('/select-events', methods=['GET', 'POST'])
@role_required("both")
def select_events():
    if request.method == 'POST':
        event = request.form.get("event")
        if event == "user":
            return redirect(url_for("user_events.user_events"))
            # return render_template("auth/select-events.html")
        elif event == "source":
            return redirect(url_for("event.source", sourceId=0))
        else:
            return render_template("auth/select-events.html", no_search=True)
    return render_template("auth/select-events.html", no_search=True)

@bp.before_app_request
def load_logged_in_user_info():
    if session.get("access") is None:
        g.user = None
    else:
        g.user = {}
        g.user["access"] = session["access"]
        g.user["username"] = session["name"]

    # user_id = ObjectId(session.get('user_id'))

    # if user_id is None:
    #     g.user = None
    # else:
    #     g.user = find_one('user', condition={'_id': user_id})

@bp.route('/logout')
@role_required('either')
def logout():
    session.clear()
    return redirect(url_for('home.home'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if not g.user:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view
