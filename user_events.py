import traceback
import requests
from .utilities import source_utilities, notification

from flask import Flask,render_template,url_for,flash, redirect, Blueprint, request, session, current_app

from .auth import role_required

from flask import jsonify
from .utilities.user_utilities import *
from .utilities.constants import *
from flask_paginate import Pagination, get_page_args
from .config import Config

userbp = Blueprint('user_events', __name__, url_prefix=Config.URL_PREFIX+'/user-events')

@userbp.route('/', methods=['GET', 'POST'])
@role_required("user")
def user_events():
    if 'select_status' in session:
        select_status = session['select_status']
    else:
        select_status = ['pending']
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
        try:
            page, per_page, offset = get_page_args(page_parameter='page', per_page_parameter='per_page')
        except ValueError:
            page = 1
        per_page = current_app.config['PER_PAGE']
        offset = (page - 1) * per_page
        total = get_all_user_events_count(select_status)
        if page <= 0 or offset >= total:
            offset = 0
            page = 1
        posts_dic = get_all_user_events_pagination(select_status, offset, per_page)
        pagination = Pagination(page=page, per_page=per_page, total=total, css_framework='bootstrap4')


    return render_template("events/user-events.html", posts_dic = posts_dic,
                            select_status=select_status, page=page,
                            per_page=per_page, pagination=pagination,
                            isUser=True)

@userbp.route('/event/<id>',  methods=['GET'])
@role_required("user")
def user_an_event(id):
    post = find_user_event(id)
    # transfer targetAudience into targetAudienceMap format
    # if ('targetAudience' in post):
    #     targetAudience_origin_list = post['targetAudience']
    #     targetAudience_edit_list = []
    #     for item in targetAudience_origin_list:
    #         if item == "faculty":
    #             targetAudience_edit_list += ["Faculty/Staff"]
    #         elif item == "staff":
    #             pass
    #         else:
    #             targetAudience_edit_list += [item.capitalize()]
    #     post['targetAudience'] = targetAudience_edit_list
    return render_template("events/event.html", post = post, eventTypeMap = eventTypeMap,
                        isUser=True, apiKey=current_app.config['GOOGLE_MAP_VIEW_KEY'])

@userbp.route('/event/<id>/edit', methods=['GET', 'POST'])
@role_required("user")
def user_an_event_edit(id):
    post_by_id = find_user_event(id)
    # transfer targetAudience into targetAudienceMap format
    # if ((post_by_id['targetAudience']) != None):
    #     targetAudience_origin_list = post_by_id['targetAudience']
    #     targetAudience_edit_list = []
    #     for item in targetAudience_origin_list:
    #         if item == "faculty":
    #             targetAudience_edit_list += ["Faculty/Staff"]
    #         elif item == "staff":
    #             pass
    #         else:
    #             targetAudience_edit_list += [item.capitalize()]
    #     post_by_id['targetAudience'] = targetAudience_edit_list
    if (post_by_id['allDay'] == True):
        post_by_id['startDate'] = (datetime.strptime((post_by_id['startDate']), "%Y-%m-%dT%H:%M:%S")).date()
        post_by_id['startDate'] =post_by_id['startDate'].strftime("%Y-%m-%d")
        post_by_id['endDate'] =(datetime.strptime((post_by_id['endDate']), "%Y-%m-%dT%H:%M:%S")).date()
        post_by_id['endDate'] = post_by_id['endDate'].strftime("%Y-%m-%d")
    if request.method == 'POST':
        # first deal with contact array -> add contacts field into request form
        contacts_arrays = []
        has_contacts_in_request = False
        for key in request.form:
            if key == 'firstName[]' or key == 'lastName[]' or key == 'contactEmail[]' or key == 'contactPhone[]':
                contact_list = request.form.getlist(key)
                if len(contact_list)!=0:
                    # delete first group of empty string
                    contact_list = contact_list[1:]
                    contacts_arrays += [contact_list]
                # reasign to create contact objects
        num_of_contacts = len(contacts_arrays[0])
        contacts_dic = []
        for i in range(num_of_contacts):
            a_contact = {}
            firstName = contacts_arrays[0][i]
            lastName = contacts_arrays[1][i]
            email = contacts_arrays[2][i]
            phone = contacts_arrays[3][i]
            if firstName!="":
                a_contact['firstName'] = firstName
            if lastName!="":
                a_contact['lastName'] = lastName
            if email!="":
                a_contact['email'] = email
            if phone!="":
                a_contact['phone'] = phone
            if a_contact!={}:
                contacts_dic.append(a_contact)
        if contacts_dic!=[]:
            has_contacts_in_request = True
            post_by_id['contacts'] =  contacts_dic

        # then edit all fields
        for key in request.form:
            if key != 'firstName[]' and key != 'lastName[]' and key != 'contactEmail[]' and key != 'contactPhone[]':
                if key == "tags":
                    tags_val = request.form[key]
                    tags_list = tags_val.split(',')
                    post_by_id[key] = tags_list
                elif key == "targetAudience":
                    # edit data format into lowercase and separate faculty and staff
                    origin_list = request.form.getlist(key)
                    edit_list = []
                    for target in origin_list:
                        if target == "Faculty/Staff":
                            edit_list += ["faculty"]
                            edit_list += ["staff"]
                        else:
                            edit_list += [target.lower()]
                    post_by_id[key] = edit_list
                elif key == "location":
                    # post_by_id['location']['description'] = request.form[key]
                    address = request.form[key]
                    # geocode location address here
                    geocode_url = "https://maps.googleapis.com/maps/api/geocode/json?address={}".format(address)
                    geocode_url = geocode_url + "&key={}".format(current_app.config['GOOGLE_KEY'])
                    # Ping google for the reuslts:
                    results = requests.get(geocode_url)
                    # Results will be in JSON format - convert to dict using requests functionality
                    results = results.json()
                    if results!= None and len(results['results']) != 0 and results['status']=='OK':
                        result = results['results'][0]
                        print(result)
                        #change description
                        post_by_id['location']['description'] = result['formatted_address']
                        post_by_id['location']['latitude'] = result['geometry']['location']['lat']
                        post_by_id['location']['longitude'] = result['geometry']['location']['lng']
                else:
                    post_by_id[key] = request.form[key]

        #once edited the status is changed into "pending"
        post_by_id['eventStatus'] = 'pending'

        #last deal with deleting fields
        delete_dictionary = {}
        #delete subcategory
        if(post_by_id['category'] != "Athletics"):
            if('subcategory' in post_by_id):
                del post_by_id['subcategory']
                delete_dictionary['subcategory'] = 1
        else:
            if('subcategory' in post_by_id and (post_by_id['subcategory']==None or post_by_id['subcategory'] == "")):
                delete_dictionary['subcategory'] = 1
        #delete audience
        if ('targetAudience' in post_by_id and 'targetAudience' not in request.form):
            del post_by_id['targetAudience']
            delete_dictionary['targetAudience'] = 1
        #delete tags
        if ('tags' in post_by_id and ('tags' not in request.form or request.form['tags'] == "")):
            del post_by_id['tags']
            delete_dictionary['tags'] = 1
        #delete contacts
        if ('contacts' in post_by_id and (not has_contacts_in_request)):
            del post_by_id['contacts']
            delete_dictionary['contacts'] = 1

        update_user_event(id, post_by_id, delete_dictionary)

        # after update in database, for display, change targetAudience format back
        if ('targetAudience' in post_by_id):
            targetAudience_origin_list = post_by_id['targetAudience']
            targetAudience_edit_list = []
            for item in targetAudience_origin_list:
                if item == "faculty":
                    targetAudience_edit_list += ["Faculty/Staff"]
                elif item == "staff":
                    pass
                else:
                    targetAudience_edit_list += [item.capitalize()]
            post_by_id['targetAudience'] = targetAudience_edit_list

        return render_template("events/event.html", post = post_by_id, eventTypeMap = eventTypeMap, isUser=True, apiKey=current_app.config['GOOGLE_MAP_VIEW_KEY'])

    tags_text = ""
    if 'tags' in post_by_id and post_by_id['tags'] != None:
        for i in range(0,len(post_by_id['tags'])):
            tags_text += post_by_id['tags'][i]
            if i!= len(post_by_id['tags']) - 1:
                tags_text += ","
    audience_dic = {}
    if 'targetAudience' in post_by_id and post_by_id['targetAudience'] != None:
        for audience in targetAudienceMap:
            audience_dic[audience] = 0
        for audience_select in post_by_id['targetAudience']:
            audience_dic[audience_select] = 1

    return render_template("events/event-edit.html", post = post_by_id, eventTypeMap = eventTypeMap,
     eventTypeValues = eventTypeValues,subcategoriesMap = subcategoriesMap, targetAudienceMap = targetAudienceMap,
     isUser=True, tags_text = tags_text, audience_dic = audience_dic, apiKey=current_app.config['GOOGLE_MAP_VIEW_KEY'])


@userbp.route('/event/<id>/approve', methods=['POST'])
@role_required("user")
def user_an_event_approve(id):
    success = False
    try:
        # So far, we do not have any information about user event image.
        # By default, we will not upload user images and we will set user image upload to be False
        success = publish_user_event(id)
        if success:
            approve_user_event(id)
    except Exception:
        traceback.print_exc()
    if success:
        return "success", 200
    else:
        return "failed", 200

@userbp.route('/event/<id>/disapprove', methods=['POST'])
@role_required("user")
def user_an_event_disapprove(id):
    try:
        disapprove_user_event(id)
    except Exception:
        traceback.print_exc()

    return "success", 200

@userbp.route('/select', methods=['POST'])
@role_required("user")
def select():
    select_status = []
    if request.form.get('approved') == '1':
        select_status.append('approved')
    if request.form.get('disapproved') == '1':
        select_status.append('disapproved')
    if request.form.get('published') == '1':
        select_status.append('published')
    if request.form.get('pending') == '1':
        select_status.append('pending')

    session["select_status"] = select_status
    return "", 200

@userbp.route('/event/add', methods=['GET', 'POST'])
@role_required("user")
def add_new_event():
    if request.method == 'POST':
        new_event = populate_event_from_form(request.form)
        new_event_id = create_new_user_event(new_event)
        return redirect(url_for('user_events.user_an_event', id=new_event_id))
    else:
        return render_template("events/add-new-event.html", eventTypeMap=eventTypeMap,
                                eventTypeValues=eventTypeValues,
                                subcategoriesMap=subcategoriesMap,
                                targetAudienceMap=targetAudienceMap)

@userbp.route('/event/<id>/notification', methods=['POST'])
@role_required("user")
def notification_event(id):
    title = request.form.get('title')
    message = request.form.get('message')
    data = {"type": "event_detail", "event_id": id}
    tokens = request.form.get('tokens').split(",")
    print("notification: event id: %s , title: %s, message body: %s" % (id, title, message))
    # send notification
    notification.send_notification(title, message, data, tokens)
    return "", 200

@userbp.route('/event/<id>/devicetokens', methods=['GET'])
@role_required("user")
def get_devicetokens(id):
    devicetokens = notification.get_favorite_eventid_information(id)
    return jsonify(devicetokens), 200

@userbp.route('/event/<id>/delete', methods=['DELETE'])
@role_required("user")
def userevent_delete(id):
    print("delete user event id: %s" % id)
    delete_user_event(id)
    return "", 200