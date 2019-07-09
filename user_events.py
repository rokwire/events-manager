import traceback
from .utilities import source_utilities

from flask import Flask,render_template,url_for,flash, redirect, Blueprint, request, session, current_app
from .utilities.user_utilities import *
from .utilities.constants import *
from flask_paginate import Pagination, get_page_args

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
        page, per_page, offset = get_page_args(page_parameter='page', per_page_parameter='per_page')
        per_page = current_app.config['PER_PAGE']
        offset = (page - 1) * per_page
        posts_dic = get_all_user_events_pagination(select_status, offset, per_page)
        total = get_all_user_events_count(select_status)
        pagination = Pagination(page=page, per_page=per_page, total=total, css_framework='bootstrap4')


    return render_template("events/user-events.html", posts_dic = posts_dic, select_status=select_status, page=page, per_page=per_page, pagination=pagination)

@userbp.route('/event/<id>',  methods=['GET'])
def user_an_event(id):
    post = find_user_event(id)
    return render_template("events/event.html", post = post, eventTypeMap = eventTypeMap,
                        isUser=True, apiKey=current_app.config['GOOGLE_MAP_VIEW_KEY'])

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
            if key == "tags" or key == "targetAudience":
                tags_val = request.form[key]
                tags_list = tags_val.split(',')
                print(tags_list)
                post_by_id[key] = tags_list
            else:
                post_by_id[key] = request.form[key]
            # 'titleURL' 'category' 'subcategory' 'startDate' 'endDate' 'cost' 'sponsor' 'description'
            # more parts editable TODO ....
        post_by_id['eventStatus'] = 'pending'
        delete_subcategory = None
        if(post_by_id['category'] != "Athletics"):
            if('subcategory' in post_by_id):
                del post_by_id['subcategory']
                delete_subcategory = {'subcategory': 1}
        else:
            if('subcategory' in post_by_id and (post_by_id['subcategory']==None or post_by_id['subcategory'] == "")):
                delete_subcategory = {'subcategory': 1}
        update_user_event(id, post_by_id, delete_subcategory)
        return render_template("events/event.html", post = post_by_id, eventTypeMap = eventTypeMap, isUser=True, apiKey=current_app.config['GOOGLE_MAP_VIEW_KEY'])

    tags_text = ""
    if 'tags' in post_by_id:
        for i in range(0,len(post_by_id['tags'])):
            tags_text += post_by_id['tags'][i]
            if i!= len(post_by_id['tags']) - 1:
                tags_text += ","

    audience_text = ""
    if 'targetAudience' in post_by_id:
        for i in range(0,len(post_by_id['targetAudience'])):
            audience_text += post_by_id['targetAudience'][i]
            if i!= len(post_by_id['targetAudience']) - 1:
                audience_text += ","

    return render_template("events/event-edit.html", post = post_by_id, eventTypeMap = eventTypeMap,
     eventTypeValues = eventTypeValues,subcategoriesMap = subcategoriesMap,
     isUser=True, tags_text = tags_text, audience_text = audience_text)

@userbp.route('/event/<id>/approve', methods=['POST'])
def user_an_event_approve(id):
    try:
        update_user_event(id, {"eventStatus": "approved"})
        # So far, we do not have any information about user event image.
        # By default, we will not upload user images and we will set user image upload to be False
        source_utilities.publish_event(id, False)
    except Exception:
        traceback.print_exc()

    return "success", 200

@userbp.route('/event/<id>/disapprove', methods=['POST'])
def user_an_event_disapprove(id):
    try:
        update_user_event(id, {"eventStatus": "disapproved"})
    except Exception:
        traceback.print_exc()

    return "success", 200

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
