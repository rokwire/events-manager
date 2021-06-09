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

import shutil
import traceback
import requests
import json
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
    if 'from' in session:
        start = session['from']
        end = session['to']
    else:
        start = ""
        end = ""
    if 'select_status' in session:
        select_status = session['select_status']
    else:
        select_status = ['approved']
        session['select_status'] = select_status

    if request.method == 'POST':
		#format : 'eventId=1234' /'category=Academic'/'eventId=1234&category=Academic'
        if 'searchInput' in request.form:
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
        if 'per_page' in request.form:
            session["per_page"] = int(request.form.get('per_page'))
            return "", 200
    else:
        try:
            page, per_page, offset = get_page_args(page_parameter='page', per_page_parameter='per_page')
        except ValueError:
            page = 1
        if 'per_page' in session:
            per_page = session['per_page']
        else:
            per_page = Config.PER_PAGE
            session['per_page'] = per_page
        offset = (page - 1) * per_page
        if 'from' in session:
            total = get_all_user_events_count(select_status, start, end)
        else:
            total = get_all_user_events_count(select_status)
        if page <= 0 or offset >= total:
            offset = 0
            page = 1
        if 'from' in session:
            posts_dic = get_all_user_events_pagination(select_status, offset, per_page, start, end)
        else:
            posts_dic = get_all_user_events_pagination(select_status, offset, per_page)
        pagination = Pagination(page=page, per_page=per_page, total=total, css_framework='bootstrap4')


    return render_template("events/user-events.html", posts_dic = posts_dic,
                            select_status=select_status, page=page,
                            per_page=per_page, pagination=pagination,
                            isUser=True, start=start, end=end, page_config=Config.EVENTS_PER_PAGE)

@userbp.route('/event/<id>',  methods=['GET'])
@role_required("user")
def user_an_event(id):
    post = find_user_event(id)
    if 'allDay' not in post:
        post['allDay'] = None
    if 'timezone' in post:
        post['startDate'] = utc_to_time_zone(post.get('timezone'), post['startDate'], post['allDay'])
    else:
        post['startDate'] = get_datetime_in_local(post.get('location'), post['startDate'], post['allDay'])
    if'endDate' in post:
        if 'timezone' in post:
            post['endDate'] = utc_to_time_zone(post.get('timezone'), post['endDate'], post['allDay'])
        else:
            post['endDate'] = get_datetime_in_local(post.get('location'), post['endDate'], post['allDay'])
    record = find_one(Config.IMAGE_COLLECTION, condition={"eventId": id})
    if len(glob(path.join(Config.WEBTOOL_IMAGE_MOUNT_POINT, id + '*'))) > 0 \
            or (record and record.get("status") == "new" or record.get("status") == "replaced"):
        post['image'] = True
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
    return render_template("events/event.html", post=post, eventTypeMap=eventTypeMap,
                           isUser=True, apiKey=current_app.config['GOOGLE_MAP_VIEW_KEY'],
                           timestamp=datetime.now().timestamp(),
                           timezones=Config.TIMEZONES)

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
        image_record = find_one(Config.IMAGE_COLLECTION, condition={"eventId": id})
        if 'file' in request.files:
            if request.files['file'].filename != '':
                for existed_file in glob(path.join(Config.WEBTOOL_IMAGE_MOUNT_POINT, id + '*')):
                    remove(existed_file)
                file = request.files['file']
                filename = secure_filename(file.filename)
                if image_record and image_record.get('status') == 'new' or image_record.get('status') == 'replaced':
                    file.save(
                        path.join(Config.WEBTOOL_IMAGE_MOUNT_POINT, id + '.' + filename.rsplit('.', 1)[1].lower()))
                    success = s3_delete_reupload(id, image_record.get("_id"))
                    if success:
                        print("{}, s3: s3_delete_reupload()".format(image_record.get('status')))
                        updateResult = update_one(current_app.config['IMAGE_COLLECTION'],
                                                     condition={'eventId': id},
                                                     update={"$set": {'status': 'replaced',
                                                                      'eventId': id}}, upsert=True)
                        post_by_id['imageURL'] = current_app.config['ROKWIRE_IMAGE_LINK_FORMAT'].format(id, image_record.get("_id"))
                        if updateResult.modified_count == 0 and updateResult.matched_count == 0 and updateResult.upserted_id is None:
                            print("Failed to mark image record as replaced of event: {} in event edit page".format(id))
                    else:
                        print("reuploading image for event:{} failed in event edit page".format(id))
                elif get_user_event_status(id) == "approved":
                    if image_record and image_record.get('status') == 'deleted':
                        updateResult = update_one(current_app.config['IMAGE_COLLECTION'],
                                                  condition={'eventId': id},
                                                  update={"$set": {'status': 'new',
                                                                   'eventId': id}}, upsert=True)
                        if updateResult.modified_count == 0 and updateResult.matched_count == 0 and updateResult.upserted_id is None:
                            print("Failed to mark image record as new of event: {} in event edit page".format(
                                id))
                    else:
                        insertResult = insert_one(current_app.config['IMAGE_COLLECTION'], document={
                            'eventId': id,
                            'status': 'new',
                        })
                        image_record = find_one(Config.IMAGE_COLLECTION, condition={"eventId": id})
                        if not insertResult.inserted_id:
                            print("Failed to mark image record as new of event: {} in event edit page".format(id))
                    file.save(
                        path.join(Config.WEBTOOL_IMAGE_MOUNT_POINT, id + '.' + filename.rsplit('.', 1)[1].lower()))
                    success = s3_image_upload(id, image_record.get("_id"))
                    if success:
                        print("{}, s3: s3_image_upload()".format(image_record.get('status')))
                        post_by_id['imageURL'] = current_app.config['ROKWIRE_IMAGE_LINK_FORMAT'].format(id, image_record.get("_id"))
                    else:
                        print("initial image upload for event:{} failed in event edit page".format(id))
                elif file and '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_IMAGE_EXTENSIONS:
                    file.save(
                        path.join(Config.WEBTOOL_IMAGE_MOUNT_POINT, id + '.' + filename.rsplit('.', 1)[1].lower()))
                else:
                    abort(400)  # TODO: Error page
        elif request.form['delete-image'] == '1':
            if image_record:
                success = s3_image_delete(id, image_record.get("_id"))
                if success:
                    print("{}, s3: s3_delete_reupload()".format(image_record.get('status')))
                    updateResult = update_one(current_app.config['IMAGE_COLLECTION'],
                                          condition={'eventId': id},
                                          update={"$set": {'status': 'deleted',
                                                           'eventId': id}}, upsert=True)
                    post_by_id['imageURL'] = ''
                    if updateResult.modified_count == 0 and updateResult.matched_count == 0 and updateResult.upserted_id is None:
                        print("Failed to mark image record as deleted of event: {} in event edit page".format(id))
                else:
                    print("deleting image for event:{} on s3 failed in event edit page".format(id))
            else:
                try:
                    remove(glob(path.join(Config.WEBTOOL_IMAGE_MOUNT_POINT, id + '*'))[0])
                except OSError:
                    print("delete event:{} image failed in ".format(id))
        all_day_event = False
        if 'allDay' in request.form and request.form.get('allDay') == 'on':
            post_by_id['allDay'] = True
            all_day_event = True
        else:
            post_by_id['allDay'] = False
        if 'isEventFree' in request.form and request.form.get('isEventFree') == 'on':
            post_by_id['isEventFree'] = True
        else:
            post_by_id['isEventFree'] = False

        if 'isVirtual' in request.form and request.form.get('isVirtual') == 'on':
            post_by_id['isVirtual'] = True
        else:
            post_by_id['isVirtual'] = False

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
                if 'timezone' in request.form:
                    post_by_id['startDate'] = time_zone_to_utc(request.form.get('timezone'), request.form.get('startDate'), 'startDate', all_day_event)
                else:
                    post_by_id['startDate'] = get_datetime_in_utc(request.form.get('location'), request.form.get('startDate'), 'startDate', all_day_event)
            elif item == 'endDate':
                end_date = request.form.get('endDate')
                if end_date != '':
                    if 'timezone' in request.form:
                        post_by_id['endDate'] = time_zone_to_utc(request.form.get('timezone'), end_date, 'endDate', all_day_event)
                    else:
                        post_by_id['endDate'] = get_datetime_in_utc(request.form.get('location'), end_date, 'endDate', all_day_event)
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

        old_sub_events = find_one(current_app.config['EVENT_COLLECTION'],
                                  condition={"_id": ObjectId(id)})['subEvents']
        new_sub_events = post_by_id['subEvents']
        if old_sub_events is not None:
            for old_sub_event in old_sub_events:
                if new_sub_events is None or old_sub_event not in new_sub_events:
                    update_super_event_id(old_sub_event['id'], '')
        if new_sub_events is not None:
            for new_sub_event in new_sub_events:
                if old_sub_events is None or new_sub_event not in old_sub_events:
                    update_super_event_id(new_sub_event['id'], id)

        old_title = find_one(current_app.config['EVENT_COLLECTION'],
                                  condition={"_id": ObjectId(id)})['title']
        new_title = post_by_id['title']
        # Special case for changing title of sub-events in super-event's page.
        if old_title != new_title:
            try:
                sub_event_list = find_one(current_app.config['EVENT_COLLECTION'], condition={"_id": ObjectId(find_one(
                    current_app.config['EVENT_COLLECTION'], condition={"_id": ObjectId(id)})['superEventID'])})['subEvents']
                for sub_event in sub_event_list:
                    if sub_event['id'] == find_one(current_app.config['EVENT_COLLECTION'], condition={"_id": ObjectId(id)})['platformEventId']:
                        sub_event['name'] = new_title
                        updateResult = update_one(current_app.config['EVENT_COLLECTION'], condition={"_id": ObjectId(post_by_id['superEventID'])},
                                                  update={
                                                      "$set": {"subEvents": sub_event_list}
                                                  })
                        if updateResult.modified_count == 0 and updateResult.matched_count == 0 and updateResult.upserted_id is None:
                            print("Failed to update the title of sub-event {} in super event {}".format(id, post_by_id['superEventID']))
            except Exception as ex:
                pass

        if 'timezone' in request.form:
            post_by_id['timezone'] = request.form['timezone']
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

        if 'timezone' in post_by_id:
            post_by_id['startDate'] = utc_to_time_zone(post_by_id.get('timezone'), post_by_id['startDate'], all_day_event)
        else:
            post_by_id['startDate'] = get_datetime_in_local(post_by_id.get('location'), post_by_id['startDate'], all_day_event)
        if 'endDate' in post_by_id:
            if 'timezone' in post_by_id:
                post_by_id['endDate'] = utc_to_time_zone(post_by_id.get('timezone'), post_by_id['endDate'], all_day_event)
            else:
                post_by_id['endDate'] = get_datetime_in_local(post_by_id.get('location'), post_by_id['endDate'], all_day_event)

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
        try:
            image_name = glob(path.join(Config.WEBTOOL_IMAGE_MOUNT_POINT, id + '*'))[0].rsplit('/', 1)[1]
            image = True
        except IndexError:
            image_name = ""
            image_record = find_one(Config.IMAGE_COLLECTION, condition={"eventId": id})
            if image_record and image_record.get('status') == "replaced" or image_record.get('status') == "new":
                image = True
            else:
                image = False
        return render_template("events/event-edit.html", post=post_by_id, eventTypeMap=eventTypeMap,
                               eventTypeValues=eventTypeValues, subcategoriesMap=subcategoriesMap,
                               targetAudienceMap=targetAudienceMap, isUser=True, tags_text=tags_text,
                               audience_dic=audience_dic, apiKey=current_app.config['GOOGLE_MAP_VIEW_KEY'],
                               extensions=",".join("." + extension for extension in Config.ALLOWED_IMAGE_EXTENSIONS),
                               image = image,
                               size_limit=Config.IMAGE_SIZE_LIMIT,
                               timezones=Config.TIMEZONES)


@userbp.route('/event/<id>/approve', methods=['POST'])
@role_required("user")
def user_an_event_approve(id):
    success = False
    try:
        # So far, we do not have any information about user event image.
        # By default, we will not upload user images and we will set user image upload to be False
        image = False
        if len(glob(path.join(Config.WEBTOOL_IMAGE_MOUNT_POINT, id + '*'))) > 0:
            image = True
        success = publish_user_event(id)
        if success and image:
            updateResult = update_one(current_app.config['IMAGE_COLLECTION'],
                                      condition={'eventId': id},
                                      update={"$set": {'status': 'new',
                                                       'eventId': id}}, upsert=True)
            if updateResult.modified_count == 0 and updateResult.matched_count == 0 and updateResult.upserted_id is None:
                print("Failed to mark image record as new of event: {} upon event publishing".format(id))
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
    if request.form.get('hide_past') == '1':
        select_status.append('hide_past')

    session["select_status"] = select_status
    return "", 200


@userbp.route('/time_range', methods=['POST'])
@role_required("user")
def time_range():
    session["from"] = request.form.get('from')
    session["to"] = request.form.get('to')
    return "", 200


@userbp.route('/event/add', methods=['GET', 'POST'])
@role_required("user")
def add_new_event():
    if request.method == 'POST':
        new_event = populate_event_from_form(request.form, session["email"])
        new_event_id = create_new_user_event(new_event)
        if new_event['subEvents'] is not None:
            for subEvent in new_event['subEvents']:
                update_super_event_id(subEvent['id'], new_event_id)
        if 'file' in request.files and request.files['file'].filename != '':
            file = request.files['file']
            filename = secure_filename(file.filename)
            if file and '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_IMAGE_EXTENSIONS:
                file.save(path.join(Config.WEBTOOL_IMAGE_MOUNT_POINT,
                                    str(new_event_id) + '.' + filename.rsplit('.', 1)[1].lower()))
            else:
                abort(400)  #TODO: Error page
        return redirect(url_for('user_events.user_an_event', id=new_event_id))
    else:
        return render_template("events/add-new-event.html", 
                                isUser=True,
                                eventTypeMap=eventTypeMap,
                                eventTypeValues=eventTypeValues,
                                subcategoriesMap=subcategoriesMap,
                                targetAudienceMap=targetAudienceMap,
                                extensions=",".join("." + extension for extension in Config.ALLOWED_IMAGE_EXTENSIONS),
                                size_limit=Config.IMAGE_SIZE_LIMIT,
                                timezones=Config.TIMEZONES)

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
    sub_events = find_one(current_app.config['EVENT_COLLECTION'], condition={"_id": ObjectId(id)}).get('subEvents')
    if sub_events is not None:
        for sub_event in sub_events:
            update_super_event_id(sub_event['id'], '')
    if get_user_event_status(id) == "approved":
        super_events = find_all(current_app.config['EVENT_COLLECTION'],
                                filter={"subEvents": {'$type': 'array'}},
                                projection={"_id": 1, "subEvents": 1})
        platform_id = find_one(current_app.config['EVENT_COLLECTION'],
                                condition={"_id": ObjectId(id)})['platformEventId']
        find = False
        for super_event in super_events:
            if find:
                break
            for sub_event in super_event['subEvents']:
                if sub_event['id'] == platform_id:
                    new_sub_events = super_event['subEvents']
                    new_sub_events.remove(sub_event)
                    update_one(current_app.config['EVENT_COLLECTION'],
                               condition={"_id": ObjectId(super_event['_id'])},
                               update={"$set": {"subEvents": new_sub_events}})

                    if get_user_event_status(super_event['_id']) == "approved":
                        success = put_user_event(super_event['_id'])
                        if not success:
                            print("updating super event in building block failed")
                    find = True
                    break
    delete_user_event(id)
    if len(glob(path.join(Config.WEBTOOL_IMAGE_MOUNT_POINT, id + '*'))) > 0:
        try:
            remove(glob(path.join(Config.WEBTOOL_IMAGE_MOUNT_POINT, id + '*'))[0])
        except OSError:
            print("delete event:{} image failed".format(id))
    record = find_one(Config.IMAGE_COLLECTION, condition={"eventId": id})
    if record:
        success = s3_image_delete(id, record.get("_id"))
        if success:
            print("{}, s3: s3_image_delete()".format(record.get('status')))
            updateResult = update_one(current_app.config['IMAGE_COLLECTION'],
                                      condition={'eventId': id},
                                      update={"$set": {'status': 'deleted',
                                                       'eventId': id}}, upsert=True)
            if updateResult.modified_count == 0 and updateResult.matched_count == 0 and updateResult.upserted_id is None:
                print("Failed to mark image record as deleted of event: {} in the deletion of event".format(id))
        else:
            print("deleting image for event:{} failed in event deletion".format(id))
    return "", 200

@userbp.route('/search', methods=['GET', 'POST'])
@role_required('user')
def search():
    if request.method == "GET":
       search_term = request.values.get("data")
       return jsonify(beta_search(search_term))
    else:
       return jsonify([]), 200


@userbp.route('/searchsub', methods=['GET'])
@role_required('user')
def searchsub():
    if request.method == "GET":
       search_term = request.values.get("data")
       return jsonify(beta_search(search_term))
    else:
       return jsonify([]), 200

@userbp.route('/event/<id>/image', methods=['GET'])
@role_required("user")
def view_image(id):
    record = find_one(Config.IMAGE_COLLECTION, condition={"eventId": id})
    if record:
        success = s3_image_download(id, record.get("_id"))
        if success:
            try:
                print("{}, s3: s3_image_download()".format(record.get('status')))
                path_to_tmp_image = os.path.join(os.getcwd(), 'temp', id + ".jpg")

                def get_image():
                    with open(path_to_tmp_image, 'rb') as f:
                        yield from f
                    os.remove(path_to_tmp_image)

                response = current_app.response_class(get_image(), mimetype='image/jpg')
                return response
            except Exception:
                traceback.print_exc()
                print("returning image for event:{} on s3 to user failed".format(id))
        else:
            abort(404)
    else:
        try:
            image_name = glob(path.join(Config.WEBTOOL_IMAGE_MOUNT_POINT, id + '*'))[0].rsplit('/', 1)[1]
            directory = path.join(getcwd(), Config.WEBTOOL_IMAGE_MOUNT_POINT.rsplit('/', 1)[1])
            return send_from_directory(directory, image_name)
        except IndexError:
            abort(404)

@userbp.route('/event/publish/<platformEventId>',  methods=['GET'])
@role_required("user")
def sub_event(platformEventId):
    try:
        eventId = clickable_utility(platformEventId)
        return redirect(url_for('user_events.user_an_event', id=eventId))

    except Exception:
        traceback.print_exc()
        print("Redirect for platformEventId {} failed".format(platformEventId))
        abort(500)
