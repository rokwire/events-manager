import traceback
from .utilities import source_utilities

from flask import Flask,render_template,url_for,flash, redirect, Blueprint, request
from .utilities.user_utilities import *
from .utilities.constants import *

userbp = Blueprint('user_events', __name__, url_prefix='/user-events')

@userbp.route('/', methods=['GET', 'POST'])
def user_events():
    if request.method == 'POST':
		#format : 'eventId=1234' /'category=Academic'/'eventId=1234&category=Academic'
        searchInput = request.form['searchInput']
        query_dic = {}
        search_list = searchInput.split('&')
        for search in search_list:
            params = search.split('=')
            if params and len(params) == 2:
                key = params[0]
                value = params[1]
                query_dic[key] = value
        posts = get_searched_user_events(query_dic)
    else:
        posts = get_all_user_events()
    return render_template("events/user-events.html", posts=posts)

@userbp.route('/event/<id>',  methods=['GET'])
def user_an_event(id):
    post = find_user_event(id)
    return render_template("events/event.html", post = post, eventTypeMap = eventTypeMap, isUser=True)

@userbp.route('/event/<id>/edit', methods=['GET', 'POST'])
def user_an_event_edit(id):
    post_by_id = find_user_event(id)
    # create dic for eventType values - new category
    eventTypeValues = {}
    for key in eventTypeMap:
        value = eventTypeMap[key]
        eventTypeValues[value] = 0
    if request.method == 'POST':
        # change the specific event
        post_by_id['titleURL'] = request.form['titleURL']
        post_by_id['subcategory'] = request.form['subcategory']
        post_by_id['startDate'] = request.form['startDate']
        post_by_id['endDate'] = request.form['endDate']
        post_by_id['cost'] = request.form['cost']
        post_by_id['sponsor'] = request.form['sponsor']
        # more parts editable TODO ....

        update_user_event(id, post_by_id)


    return render_template("events/event-edit.html", post = post_by_id, eventTypeMap = eventTypeMap, eventTypeValues = eventTypeValues, isUser=True)

@userbp.route('/event/<id>/approve')
def user_an_event_approve(id):
    try:
        update_user_event(id, {"eventStatus": "approved"})
        source_utilities.publish_event(id)
    except Exception:
        traceback.print_exc()

    return redirect(url_for("user_events.user_an_event", id=id))
