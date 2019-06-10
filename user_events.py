from flask import Flask,render_template,url_for,flash, redirect, Blueprint, request
from .utilities.user_utilities import *
from .utilities.constants import *

userbp = Blueprint('user_events', __name__, url_prefix='/user-events')

@userbp.route('/')
def user_events():
    posts = get_all_user_events()
    return render_template("events/user-events.html", posts=posts)

@userbp.route('/event<id>',  methods=['GET'])
def user_an_event(id):
    post = find_user_event(id)
    return render_template("events/event.html", post = post)

@userbp.route('/event<id>/edit', methods=['GET', 'POST'])
def user_an_event_edit(id):
    post_by_id = find_user_event(id)
    if request.method == 'POST':
        # change the specific event
        post_by_id['titleURL'] = request.form['titleURL']
        post_by_id['startDate'] = request.form['startDate']
		post_by_id['endDate'] = request.form['endDate']
        post_by_id['cost'] = request.form['cost']
        post_by_id['sponsor'] = request.form['sponsor']
        # more parts editable TODO ....

        # insert update_user_event function here later
        update_user_event(id, post_by_id)
    return render_template("events/event-edit.html", post = post_by_id, eventTypeMap = eventTypeMap)
