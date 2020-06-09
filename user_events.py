import shutil
import traceback
import requests
from .utilities import source_utilities, notification

from flask import Flask, render_template, url_for, flash, redirect, Blueprint, request, session, current_app, \
    send_from_directory, abort

from .auth import role_required

from flask import jsonify
from .utilities.user_utilities import *
from .utilities.constants import *
from flask_paginate import Pagination, get_page_args
from .config import Config
from werkzeug.utils import secure_filename
from glob import glob
from os import remove, path, getcwd, makedirs

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
    post['startDate'] = get_datetime_in_local(post['startDate'], post['allDay'])
    if'endDate' in post:
        post['endDate'] = get_datetime_in_local(post['endDate'], post['allDay'])
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
    post['longDescription'] = post['longDescription'].replace("\n", "<br>")
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

    # POST Method
    if request.method == 'POST':
        super_event_checked = False
        post_by_id['contacts'] = get_contact_list(request.form)
        post_by_id['tags'] = get_tags(request.form)
        post_by_id['targetAudience'] = get_target_audience(request.form)

        if 'file' in request.files and request.files['file'].filename != '':
            if not path.exists(path.join(Config.WEBTOOL_IMAGE_MOUNT_POINT, id)):
                makedirs(path.join(Config.WEBTOOL_IMAGE_MOUNT_POINT, id))
            for existed_file in glob(path.join(Config.WEBTOOL_IMAGE_MOUNT_POINT, id, '*')):
                remove(existed_file)
            file = request.files['file']
            filename = secure_filename(file.filename)
            if file and '.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_IMAGE_EXTENSIONS:
                file.save(path.join(Config.WEBTOOL_IMAGE_MOUNT_POINT, id, filename))
            else:
                abort(400)  # TODO: Error page
        all_day_event = False
        if 'allDay' in request.form and request.form.get('allDay') == 'on':
            post_by_id['allDay'] = True
            all_day_event = True
        else:
            post_by_id['allDay'] = False

        for item in request.form:
            if item == 'title'and item != None:
                post_by_id['title'] = request.form[item]
            elif item == 'titleURL':
                post_by_id['titleURL'] = request.form[item]
            elif item == 'category':
                post_by_id['category'] = request.form[item]
            elif item == 'cost':
                post_by_id['cost'] = request.form[item]
            elif item == 'sponsor':
                post_by_id['sponsor'] = request.form[item]
            elif item == 'longDescription':
                post_by_id['longDescription'] = request.form[item]
            elif item == 'isSuperEvent':
                if request.form[item] == 'on':
                    super_event_checked = True
                    post_by_id['isSuperEvent'] = True
                else:
                    post_by_id['isSuperEvent'] = False
            elif item == 'startDate':
                post_by_id['startDate'] = get_datetime_in_utc(request.form.get('startDate'), 'startDate', all_day_event)
            elif item == 'endDate':
                end_date = request.form.get('endDate')
                if end_date != '':
                    post_by_id['endDate'] = get_datetime_in_utc(end_date, 'endDate', all_day_event)
                elif 'endDate' in post_by_id:
                    del post_by_id['endDate']
            elif item == 'location':
                location = request.form.get('location')
                if location != '':
                    post_by_id['location'] = get_location_details(location)
                else:
                    post_by_id['location'] = None

        if post_by_id['category'] == "Athletics":
            post_by_id['subcategory'] = request.form['subcategory']
        else:
            post_by_id['subcategory'] = None

        if super_event_checked == False:
            post_by_id['isSuperEvent'] = False
        if post_by_id['isSuperEvent'] == True :
            post_by_id['subEvents'] = get_subevent_list(request.form)
        else:
            post_by_id['subEvents'] = None

        update_user_event(id, post_by_id, None)

        # Check for event status
        event_status = get_user_event_status(id)
        if event_status == "approved":
            success = put_user_event(id)
            if not success:
                return "fail", 200
        
        return redirect(url_for('user_events.user_an_event', id=id))

    # GET method
    elif request.method == 'GET':

        all_day_event = False
        if 'allDay' in post_by_id and post_by_id['allDay'] is True:
            all_day_event = True

        post_by_id['startDate'] = get_datetime_in_local(post_by_id['startDate'], all_day_event)
        if 'endDate' in post_by_id:
            post_by_id['endDate'] = get_datetime_in_local(post_by_id['endDate'], all_day_event)

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

        return render_template("events/event-edit.html", post=post_by_id, eventTypeMap=eventTypeMap,
                               eventTypeValues=eventTypeValues, subcategoriesMap=subcategoriesMap,
                               targetAudienceMap=targetAudienceMap, isUser=True, tags_text=tags_text,
                               audience_dic=audience_dic, apiKey=current_app.config['GOOGLE_MAP_VIEW_KEY'],
                               extensions=",".join("." + extension for extension in Config.ALLOWED_IMAGE_EXTENSIONS))


@userbp.route('/event/<id>/approve', methods=['POST'])
@role_required("user")
def user_an_event_approve(id):
    success = False
    try:
        # So far, we do not have any information about user event image.
        # By default, we will not upload user images and we will set user image upload to be False
        success_1 = publish_user_event(id)
        #success_2 = publish_image(id)
        if success_1:
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
        new_event = populate_event_from_form(request.form, session["email"])
        new_event_id = create_new_user_event(new_event)
        # if 'file' not in request.files:
        #     return jsonify({"code": -1, "message": "No file in request"})
        # if file.filename == '':
        #     return jsonify({"code": -1, "message": "No selected file"})
        if 'file' in request.files and request.files['file'].filename != '':
            file = request.files['file']
            filename = secure_filename(file.filename)
            if file and '.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_IMAGE_EXTENSIONS:
                if not path.exists(path.join(Config.WEBTOOL_IMAGE_MOUNT_POINT, str(new_event_id))):
                    makedirs(path.join(Config.WEBTOOL_IMAGE_MOUNT_POINT, str(new_event_id)))
                file.save(path.join(Config.WEBTOOL_IMAGE_MOUNT_POINT, str(new_event_id), filename))
            else:
                abort(400)  #TODO: Error page
        return redirect(url_for('user_events.user_an_event', id=new_event_id))
    else:
        return render_template("events/add-new-event.html", eventTypeMap=eventTypeMap,
                                eventTypeValues=eventTypeValues,
                                subcategoriesMap=subcategoriesMap,
                                targetAudienceMap=targetAudienceMap,
                                extensions=",".join("." + extension for extension in Config.ALLOWED_IMAGE_EXTENSIONS))

@userbp.route('/event/<id>/notification', methods=['POST'])
@role_required("user")
def notification_event(id):
    title = request.form.get('title')
    message = request.form.get('message')
    data = {"type": "event_detail", "event_id": id}
    tokens = request.form.get('tokens').split(",")
    print("notification: event platform id: %s , title: %s, message body: %s" % (id, title, message))
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
    shutil.rmtree(path.join(Config.WEBTOOL_IMAGE_MOUNT_POINT, id))
    return "", 200


@userbp.route('/event/<id>/image', methods=['GET'])
@role_required("user")
def view_image(id):
    try:
        image_name = glob(path.join(Config.WEBTOOL_IMAGE_MOUNT_POINT, id, '*'))[0].rsplit('/', 1)[1]
        directory = path.join(getcwd(), Config.WEBTOOL_IMAGE_MOUNT_POINT.rsplit('/', 1)[1], id)
        return send_from_directory(directory, image_name)
    except IndexError:
        abort(404)

# @userbp.route('/event/upload_image', methods=['PUT'])
# @role_required("user")
# def upload_image():
#     if 'file' not in request.files:
#         return jsonify({"code": -1, "message": "No 'file' in request", "hash": None})
#     file = request.files['file']
#     if file.filename == '':
#         return jsonify({"code": -1, "message": "No selected file", "hash": None})
#     if file and allowed_file(file.filename):
#         image_hash = sha256((file.filename + str(datetime.now().timestamp())).encode('utf-8')).hexdigest()
#         filename = image_hash + '.' + secure_filename(file.filename).rsplit('.', 1)[1]
#         file.save(path.join(Config.WEBTOOL_IMAGE_MOUNT_POINT, filename))
#         return jsonify({"code": 0, "message": "image uploaded", "hash": image_hash})
#     else:
#         return jsonify({"code": -1, "message": "file type not allowed", "hash": None})
