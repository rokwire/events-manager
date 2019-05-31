from flask import Flask,render_template,url_for,flash, redirect, Blueprint
from utilities.user_utilities import *

userbp = Blueprint('user_events', __name__, url_prefix='/user-events')

@userbp.route('/')
def user_events():
    return render_template("events/user-events.html", posts=posts)

@userbp.route('/event<id>',  methods=['GET'])
def user_an_event(id):
	return render_template("events/event.html", post = find_user_event(id, posts))

@userbp.route('/event<id>/edit', methods=['GET', 'POST'])
def user_an_event_edit(id):
    return render_template("events/event-edit.html", post = find_user_event(id, posts))
