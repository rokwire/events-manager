import traceback
from .utilities import source_utilities

from flask import Flask,render_template,url_for,flash, redirect, Blueprint, request, session
from .utilities.user_utilities import *
from .utilities.constants import *

userbp = Blueprint('user_events', __name__, url_prefix='/user-events')

@userbp.route('/', methods=['GET', 'POST'])
def user_events():
    if 'select_status' in session:
        select_status = session['select_status']
    else:
        select_status = []
        session['select_status'] = select_status

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
        posts = get_searched_user_events(query_dic, select_status)
    else:
        posts = get_all_user_events(select_status)
    return render_template("events/user-events.html", posts=posts, select_status=select_status)

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
        # print(request.form)
        for key in request.form:
            post_by_id[key] = request.form[key]
            # 'titleURL' 'category' 'subcategory' 'startDate' 'endDate' 'cost' 'sponsor' 'description'
            # more parts editable TODO ....
        post_by_id['eventStatus'] = 'pending'
        if(post_by_id['category'] != "Athletics"):
            if(post_by_id['subcategory']!=None):
                post_by_id['subcategory']=None
        update_user_event(id, post_by_id)
        return render_template("events/event.html", post = post_by_id, eventTypeMap = eventTypeMap, isUser=True)

    return render_template("events/event-edit.html", post = post_by_id, eventTypeMap = eventTypeMap, eventTypeValues = eventTypeValues,subcategoriesMap = subcategoriesMap, isUser=True)

@userbp.route('/event/<id>/approve')
def user_an_event_approve(id):
    try:
        update_user_event(id, {"eventStatus": "approved"})
        source_utilities.publish_event(id)
    except Exception:
        traceback.print_exc()

    return redirect(url_for("user_events.user_an_event", id=id))


@userbp.route('/select', methods=['POST'])
def select():
    select_status = []
    if request.form.get('approved') == '1':
        select_status.append('approved')
    if request.form.get('disapproved') == '1':
        select_status.append('disapproved')
    if request.form.get('published') == '1':
        select_status.append('published')

    session["select_status"] = select_status
    return "", 200
