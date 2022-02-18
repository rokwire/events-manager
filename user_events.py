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
from datetime import datetime, timedelta
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

import logging
from time import gmtime

logging.Formatter.converter = gmtime
logging.basicConfig(level=logging.INFO, datefmt='%Y-%m-%dT%H:%M:%S',
                    format='%(asctime)-15s.%(msecs)03dZ %(levelname)-7s [%(threadName)-10s] : %(name)s - %(message)s')
__logger = logging.getLogger("user_events.py")

userbp = Blueprint('user_events', __name__, url_prefix=Config.URL_PREFIX+'/user-events')

@userbp.route('/', methods=['GET', 'POST'])
@role_required("user")
def user_events():
    if 'from' in session:
        start = session['from']
        end = session['to']
        start_date_filter = start
        end_date_filter = end
        if start:
            start_date_filter = datetime.strptime(start, '%Y-%m-%d').strftime('%Y-%m-%dT%H:%M:%S')
        if end:
            end_date_filter = (datetime.strptime(end, '%Y-%m-%d')+timedelta(hours=23,minutes=59, seconds=59)).strftime('%Y-%m-%dT%H:%M:%S')
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
        if 'group' in request.form:
            session["group"] = str(request.form.get('group'))
        return "", 200
    else:
        groups, _ = get_admin_groups()
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
            group_ids = get_admin_group_ids()
            if "group" in session and session["group"] != 'all':
                group_ids = [session["group"]]
            total = get_all_user_events_count(group_ids, select_status, start_date_filter, end_date_filter)
        else:
            group_ids = get_admin_group_ids()
            if "group" in session and session["group"] != 'all':
                group_ids = [session["group"]]
            total = get_all_user_events_count(group_ids, select_status)
        if page <= 0 or offset >= total:
            offset = 0
            page = 1
        if 'from' in session:
            #Modifications
            group_ids = get_admin_group_ids()
            if "group" in session and session["group"] != 'all':
                group_ids = [session["group"]]
            posts_dic = get_all_user_events_pagination(group_ids, select_status, offset, per_page, start_date_filter, end_date_filter)
        else:
            #Modifications
            group_ids = get_admin_group_ids()
            if "group" in session and session["group"] != 'all':
                group_ids = [session["group"]]
            posts_dic = get_all_user_events_pagination(group_ids, select_status, offset, per_page)
        for list in posts_dic.values():
            post = list[0]
            if 'timezone' in post:
                post['startDate'] = utc_to_time_zone(post.get('timezone'), post['startDate'], post['allDay'])
                if post['allDay']:
                    post['startDate'] = datetime.strptime(post['startDate'], '%Y-%m-%d').strftime('%m/%d/%Y')
                else:
                    post['startDate'] = datetime.strptime(post['startDate'], '%Y-%m-%dT%H:%M:%S').strftime('%m/%d/%Y %I:%M %p')
            else:
                post['startDate'] = get_datetime_in_local(post.get('location'), post['startDate'], post['allDay'])
                if post['allDay']:
                    post['startDate'] = datetime.strptime(post['startDate'], '%Y-%m-%d').strftime('%m/%d/%Y')
                else:
                    post['startDate'] = datetime.strptime(post['startDate'], '%Y-%m-%dT%H:%M:%S').strftime('%m/%d/%Y %I:%M %p')
            if 'endDate' in post:
                if 'timezone' in post:
                    post['endDate'] = utc_to_time_zone(post.get('timezone'), post['endDate'], post['allDay'])
                    if post['allDay']:
                        post['endDate'] = datetime.strptime(post['endDate'], '%Y-%m-%d').strftime('%m/%d/%Y')
                    else:
                        post['endDate'] = datetime.strptime(post['endDate'], '%Y-%m-%dT%H:%M:%S').strftime('%m/%d/%Y %I:%M %p')
                else:
                    post['endDate'] = get_datetime_in_local(post.get('location'), post['endDate'], post['allDay'])
                    if post['allDay']:
                        post['endDate'] = datetime.strptime(post['endDate'], '%Y-%m-%d').strftime('%m/%d/%Y')
                    else:
                        post['endDate'] = datetime.strptime(post['endDate'], '%Y-%m-%dT%H:%M:%S').strftime('%m/%d/%Y %I:%M %p')
        pagination = Pagination(page=page, per_page=per_page, total=total, css_framework='bootstrap4')


    return render_template("events/user-events.html", posts_dic = posts_dic,
                            select_status=select_status, page=page,
                            per_page=per_page, pagination=pagination,
                            isUser=True, start=start, end=end, page_config=Config.EVENTS_PER_PAGE,
                            groups=groups,
                            selected_group=session.get('group'))

@userbp.route('/event/<id>',  methods=['GET'])
@role_required("user")
def user_an_event(id):
    post = find_user_event(id)
    groups, _ = get_admin_groups()
    for group in groups:
        if group['id'] == post['createdByGroupId']:
            groupName = group['title']
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
    if post['subEvents']:
        # fill in missing fields: eventid, status
        # for subEvent in post['subEvents']:
        #     if 'eventid' not in subEvent:
        #         fill_missing_subevent_fileds_in_superevent(subEvent['id'], id)

        for subEvent in post['subEvents']:
            if 'id' in subEvent:
                event = find_user_event(clickable_utility(subEvent['id']))
                if event['eventStatus'] == 'approved':
                    subEvent['isPublished'] = True
                else:
                    subEvent['isPublished'] = False
            elif 'eventid' in subEvent:
                event = find_user_event(subEvent['eventid'])
                subEvent['isPublished'] = False
            else:
                post['subEvents'].remove(subEvent)
                __logger.debug("remove incorrect subevent")
                find_one_and_update(current_app.config['EVENT_COLLECTION'],
                                             condition={"_id": ObjectId(id)}, update={
                        "$set": {"subEvents": post['subEvents']}
                    })


    return render_template("events/event.html", post=post, eventTypeMap=eventTypeMap,
                           isUser=True, apiKey=current_app.config['GOOGLE_MAP_VIEW_KEY'],
                           timestamp=datetime.now().timestamp(),
                           timezones=Config.TIMEZONES,
                           groupName=groupName)

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
        deleteEndDate = False
        post_by_id['contacts'] = get_contact_list(request.form)
        if request.form['tags']:
            post_by_id['tags'] = request.form['tags'].split(',')
            for i in range(1, len(post_by_id['tags'])):
                post_by_id['tags'][i] = post_by_id['tags'][i].lstrip()
                if post_by_id['tags'][i] == '':
                    del post_by_id['tags'][i]
        post_by_id['targetAudience'] = get_target_audience(request.form)
        image_record = find_one(Config.IMAGE_COLLECTION, condition={"eventId": id})
        if 'file' in request.files and request.files['file'].filename != '':
            for existed_file in glob(path.join(Config.WEBTOOL_IMAGE_MOUNT_POINT, id + '*')):
                remove(existed_file)
            file = request.files['file']
            filename = secure_filename(file.filename)
            if image_record and image_record.get('status') == 'new' or image_record.get('status') == 'replaced':
                file.save(
                    path.join(Config.WEBTOOL_IMAGE_MOUNT_POINT, id + '.' + filename.rsplit('.', 1)[1].lower()))

                success = s3_delete_reupload(id, post_by_id.get('platformEventId'),image_record.get("_id"))
                if success:
                    __logger.info("{}, s3: s3_delete_reupload()".format(image_record.get('status')))
                    updateResult = update_one(current_app.config['IMAGE_COLLECTION'],
                                                 condition={'eventId': id},
                                                 update={"$set": {'status': 'replaced',
                                                                  'eventId': id}}, upsert=True)
                    post_by_id['imageURL'] = current_app.config['ROKWIRE_IMAGE_LINK_FORMAT'].format(post_by_id.get('platformEventId'), image_record.get("_id"))
                    if updateResult.modified_count == 0 and updateResult.matched_count == 0 and updateResult.upserted_id is None:
                        __logger.error("Failed to mark image record as replaced of event: {} in event edit page".format(id))
                else:
                    __logger.error("reuploading image for event:{} failed in event edit page".format(id))
            elif get_user_event_status(id) == "approved":
                if image_record and image_record.get('status') == 'deleted':
                    updateResult = update_one(current_app.config['IMAGE_COLLECTION'],
                                              condition={'eventId': id},
                                              update={"$set": {'status': 'new',
                                                               'eventId': id}}, upsert=True)
                    if updateResult.modified_count == 0 and updateResult.matched_count == 0 and updateResult.upserted_id is None:
                        __logger.error("Failed to mark image record as new of event: {} in event edit page".format(
                            id))
                else:
                    insertResult = insert_one(current_app.config['IMAGE_COLLECTION'], document={
                        'eventId': id,
                        'status': 'new',
                    })
                    image_record = find_one(Config.IMAGE_COLLECTION, condition={"eventId": id})
                    if not insertResult.inserted_id:
                        __logger.error("Failed to mark image record as new of event: {} in event edit page".format(id))
                file.save(
                    path.join(Config.WEBTOOL_IMAGE_MOUNT_POINT, id + '.' + filename.rsplit('.', 1)[1].lower()))
                success = s3_image_upload(id, post_by_id.get("platformEventId"), image_record.get("_id"))
                if success:
                    __logger.info("{}, s3: s3_image_upload()".format(image_record.get('status')))
                    post_by_id['imageURL'] = current_app.config['ROKWIRE_IMAGE_LINK_FORMAT'].format(post_by_id.get("platformEventId"), image_record.get("_id"))
                else:
                    __logger.error("initial image upload for event:{} failed in event edit page".format(id))
            elif file and '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_IMAGE_EXTENSIONS:
                file.save(
                    path.join(Config.WEBTOOL_IMAGE_MOUNT_POINT, id + '.' + filename.rsplit('.', 1)[1].lower()))
            else:
                abort(400)  # TODO: Error page
        elif request.form['delete-image'] == '1':
            if image_record:
                success = s3_image_delete(id, post_by_id.get("platformEventId"), image_record.get("_id"))
                if success:
                    __logger.info("{}, s3: s3_delete_reupload()".format(image_record.get('status')))
                    updateResult = update_one(current_app.config['IMAGE_COLLECTION'],
                                          condition={'eventId': id},
                                          update={"$set": {'status': 'deleted',
                                                           'eventId': id}}, upsert=True)
                    post_by_id['imageURL'] = ''
                    if updateResult.modified_count == 0 and updateResult.matched_count == 0 and updateResult.upserted_id is None:
                        __logger.error("Failed to mark image record as deleted of event: {} in event edit page".format(id))
                else:
                    __logger.error("deleting image for event:{} on s3 failed in event edit page".format(id))
            else:
                try:
                    remove(glob(path.join(Config.WEBTOOL_IMAGE_MOUNT_POINT, id + '*'))[0])
                except OSError:
                    __logger.error("delete event:{} image failed in ".format(id))
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
        if 'displayOnlyWithSuperEvent' in request.form and request.form.get('displayOnlyWithSuperEvent') == 'on':
            post_by_id['displayOnlyWithSuperEvent'] = True
        else:
            post_by_id['displayOnlyWithSuperEvent'] = False

        if 'isVirtual' in request.form and request.form.get('isVirtual') == 'on':
            post_by_id['isVirtual'] = True
        else:
            post_by_id['isVirtual'] = False

        for item in request.form:
            if item == 'createdByGroupId':
                post_by_id['createdByGroupId'] = request.form[item]
            if item == 'title'and item != None:
                post_by_id['title'] = request.form[item]
            elif item == 'titleURL':
                post_by_id['titleURL'] = request.form[item]
            elif item == 'registrationURL': #Added
                post_by_id['registrationURL'] = request.form[item] #Added
            elif item == 'registrationLabel': #Added
                post_by_id['registrationLabel'] = request.form[item] #Added
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
                if all_day_event:
                    post_by_id['startDate'] = request.form.get('startDate')
                else:
                    post_by_id['startDate'] = request.form.get('startDate') + 'T' + request.form.get('startTime')
                if 'timezone' in request.form:
                    post_by_id['startDate'] = time_zone_to_utc(request.form.get('timezone'), post_by_id['startDate'], 'startDate', all_day_event)
                else:
                    post_by_id['startDate'] = get_datetime_in_utc(request.form.get('location'), post_by_id['startDate'], 'startDate', all_day_event)
            elif item == 'endDate':
                end_date = request.form.get('endDate')
                if end_date != "" and not all_day_event:
                    end_date = request.form.get('endDate') + 'T' + request.form.get('endTime')
                if end_date != '':
                    if 'timezone' in request.form:
                        post_by_id['endDate'] = time_zone_to_utc(request.form.get('timezone'), end_date, 'endDate', all_day_event)
                    else:
                        post_by_id['endDate'] = get_datetime_in_utc(request.form.get('location'), end_date, 'endDate', all_day_event)
                elif 'endDate' in post_by_id:
                    del post_by_id['endDate']
                    deleteEndDate = True
            elif item == 'location':
                location = request.form.get('location')
                if location != '':
                    post_by_id['location'] = get_location_details(location, post_by_id.get('isVirtual'))
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
                    # unlink between subevent and super event.
                    if 'id' in old_sub_event:
                        update_super_event_by_platform_id(old_sub_event['id'], '')
                    elif 'eventid' in old_sub_event:
                        update_super_event_by_local_id(old_sub_event['eventid'], '')
                    else:
                        old_sub_events.remove(old_sub_event)
                        __logger.debug("remove incorrect subevent")
        new_added_subevents= list()
        overwrite_subevents = list()
        if new_sub_events is not None:
            removed_list = list()
            for new_sub_event in new_sub_events:
                can_add_pending = False
                try:
                    if old_sub_events is None or new_sub_event not in old_sub_events:
                        new_added_subevent = None
                        # handle published event
                        if 'id' in new_sub_event:
                            found = False
                            for old_sub_event in old_sub_events:
                                if 'id' in new_sub_event and 'id' in old_sub_event and old_sub_event["id"] == new_sub_event['id']:
                                    found = True
                                    overwrite_subevents.append(new_sub_event)
                                    break
                            if found:
                                continue
                            new_added_subevent = find_one(current_app.config['EVENT_COLLECTION'],
                                                          condition={"platformEventId": new_sub_event['id']})
                            if "superEventID" not in new_added_subevent:
                                can_add_pending = True
                                update_super_event_by_platform_id(new_sub_event['id'], id)
                        # handle pending user event.
                        elif 'eventid' in new_sub_event:
                            found = False
                            for old_sub_event in old_sub_events:
                                if 'eventid' in new_sub_event and 'eventid' in old_sub_event and old_sub_event["eventid"] == new_sub_event['eventid']:
                                    found = True
                                    overwrite_subevents.append(new_sub_event)
                                    break
                            if found:
                                continue
                            new_added_subevent = find_user_event(new_sub_event['eventid'])
                            if "superEventID" not in new_added_subevent:
                                can_add_pending = True
                                update_super_event_by_local_id(new_sub_event['eventid'], id)
                        else:
                            new_sub_events.remove(new_sub_event)
                        if can_add_pending:
                            new_added_subevents.append(new_sub_event)
                except Exception as ex:
                    removed_list.append(new_sub_event)
                    pass
            # comment out to allow add pending events to super event.
            # for deleted_sub_event in removed_list:
            #     new_sub_events.remove(deleted_sub_event)
            overwrite_subevents_to_superevent(overwrite_subevents, id)
            store_pending_subevents_to_superevent(new_added_subevents, id)
            if 'eventStatus' in post_by_id and post_by_id['eventStatus'] == 'approved':
                post_by_id['subEvents'] = publish_pending_subevents(id)
        old_title = find_one(current_app.config['EVENT_COLLECTION'],
                                  condition={"_id": ObjectId(id)})['title']

        if old_sub_events:
            for old_sub_event in old_sub_events:
                if new_sub_events is not None and old_sub_event not in new_sub_events:
                    # delete from db
                    if 'id' in old_sub_event:
                        found = False
                        for new_sub_event in new_sub_events:
                            if 'id' in new_sub_event and 'id' in old_sub_event and old_sub_event["id"] == new_sub_event['id']:
                                found = True
                                break
                        if found:
                            continue
                        remove_subevent_from_superevent_by_paltformid(old_sub_event['id'], id)
                        for subevent in post_by_id['subEvents']:
                            if 'id' in subevent and 'id' in old_sub_event and subevent['id'] == old_sub_event['id']:
                                post_by_id['subEvents'].remove(subevent)
                                break
                    else:
                        found = False
                        for new_sub_event in new_sub_events:
                            if 'eventid' in new_sub_event and old_sub_event["eventid"] == new_sub_event['eventid']:
                                found = True
                                break
                        if found:
                            continue
                        remove_subevent_from_superevent_by_eventid(old_sub_event['eventid'], id)
                        for subevent in post_by_id['subEvents']:
                            if 'eventid' in subevent and subevent['eventid'] == old_sub_event['eventid']:
                                post_by_id['subEvents'].remove(subevent)
                                break

        new_title = post_by_id['title']
        # Special case for changing title of sub-events in super-event's page.
        if old_title != new_title:
            try:
                sub_event_list = find_one(current_app.config['EVENT_COLLECTION'], condition={"_id": ObjectId(find_one(
                    current_app.config['EVENT_COLLECTION'], condition={"_id": ObjectId(id)})['superEventID'])})['subEvents']
                for sub_event in sub_event_list:
                    # if sub event is not published when added to super event, the 'status' field is missing,
                    # so we assume a sub event is published if 'status' is missing
                    if (sub_event.get('status', 'approved') == 'pending' and sub_event['eventid'] == id) \
                            or (sub_event.get('status', 'approved') == 'approved' and sub_event['id'] == find_one(current_app.config['EVENT_COLLECTION'], condition={"_id": ObjectId(id)})['platformEventId']):
                        sub_event['name'] = new_title
                        updateResult = update_one(current_app.config['EVENT_COLLECTION'], condition={"_id": ObjectId(post_by_id['superEventID'])},
                                                  update={
                                                      "$set": {"subEvents": sub_event_list}
                                                  })
                        if updateResult.modified_count == 0 and updateResult.matched_count == 0 and updateResult.upserted_id is None:
                            __logger.error("Failed to update the title of sub-event {} in super event {}".format(id, post_by_id['superEventID']))
            except Exception as ex:
                __logger.exception(ex)
                pass

        if 'timezone' in request.form:
            post_by_id['timezone'] = request.form['timezone']
        if deleteEndDate:
            update_user_event(id, post_by_id, {'endDate': ""})
        else:
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

        headers = {"ROKWIRE-API-KEY": Config.ROKWIRE_API_KEY}
        tags = requests.get(Config.EVENT_BUILDING_BLOCK_URL+"/tags", headers=headers)

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
        groups, _ = get_admin_groups()
        return render_template("events/event-edit.html", post=post_by_id, eventTypeMap=eventTypeMap,
                               eventTypeValues=eventTypeValues, subcategoriesMap=subcategoriesMap,
                               targetAudienceMap=targetAudienceMap, isUser=True, tags_text=tags_text,
                               audience_dic=audience_dic, apiKey=current_app.config['GOOGLE_MAP_VIEW_KEY'],
                               extensions=",".join("." + extension for extension in Config.ALLOWED_IMAGE_EXTENSIONS),
                               image=image,
                               size_limit=Config.IMAGE_SIZE_LIMIT,
                               timezones=Config.TIMEZONES,
                               tags=tags.json(),
                               groups=groups)


@userbp.route('/event/<id>/approve', methods=['POST'])
@role_required("user")
def user_an_event_approve(id):
    record = find_one(current_app.config['EVENT_COLLECTION'],
                                  condition={"_id": ObjectId(id)})
    if record['isSuperEvent']:
        publish_pending_subevents(id)
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
                __logger.error("Failed to mark image record as new of event: {} upon event publishing".format(id))
            approve_user_event(id)
    except Exception as ex:
        __logger.exception(ex)
    if success:
        return "success", 200
    else:
        return "failed", 200

@userbp.route('/event/<id>/disapprove', methods=['POST'])
@role_required("user")
def user_an_event_disapprove(id):
    try:
        disapprove_user_event(id)
    except Exception as ex:
        __logger.exception(ex)

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
    headers = {"ROKWIRE-API-KEY": Config.ROKWIRE_API_KEY}
    groups, _ = get_admin_groups()
    new_event_id = None
    req = requests.get(Config.EVENT_BUILDING_BLOCK_URL + "/tags", headers=headers)
    if request.method == 'POST':
        new_event = populate_event_from_form(request.form, session["email"])
        new_event['isGroupPrivate'] = False
        if new_event.get('isEventFree') == 'on':
            new_event['isEventFree'] = True
        if new_event.get('displayOnlyWithSuperEvent') == 'on':
            new_event['displayOnlyWithSuperEvent'] = True
        new_event_id = create_new_user_event(new_event)
        if new_event['subEvents'] is not None:
            for subEvent in new_event['subEvents']:
                if 'id' in subEvent:
                    update_super_event_by_platform_id(subEvent['id'], new_event_id)
                else:
                    update_super_event_by_local_id(subEvent['eventid'], new_event_id)
        if new_event['tags']:
            new_event['tags'] = new_event['tags'][0].split(',')
            for i in range(1, len(new_event['tags'])):
                new_event['tags'][i] = new_event['tags'][i].lstrip()
                if new_event['tags'][i] == '':
                    del new_event['tags'][i]
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
                                timezones=Config.TIMEZONES,
                                tags=req.json(),
                                groups=groups)

@userbp.route('/event/<id>/notification', methods=['POST'])
@role_required("user")
def notification_event(id):
    title = request.form.get('title')
    message = request.form.get('message')
    data = {"type": "event_detail", "event_id": id}
    tokens = request.form.get('tokens').split(",")
    __logger.info("notification: event platform id: %s , title: %s, message body: %s" % (id, title, message))
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
    userEvent = find_user_event(id)
    __logger.info("delete user event id: %s" % id)
    # find subevents of this event and delete
    sub_events = find_one(current_app.config['EVENT_COLLECTION'], condition={"_id": ObjectId(id)}).get('subEvents')
    if sub_events is not None:
        # this events can be subevents for multiple superevents
        for sub_event in sub_events:
            # unset each subevent
            update_super_event_id(sub_event['id'], '')

    if get_user_event_status(id) == "approved":
        # if this event is a subevent, need to unset this event from all its superevents
        # get all superevents which has atleast one subevent. check if the event_platformid is same as subevent_id of superevents
        super_events = find_all(current_app.config['EVENT_COLLECTION'],
                                filter={"subEvents": {'$type': 'array'}},
                                projection={"_id": 1, "subEvents": 1})
        platform_id = find_one(current_app.config['EVENT_COLLECTION'],
                                condition={"_id": ObjectId(id)})['platformEventId']
        # TODO: change this logic to access superEventID field of the subevent to delete the event.
        for super_event in super_events:
            for sub_event in super_event['subEvents']:
                if sub_event['id'] == platform_id:
                    # get all subevents, except for the current event
                    new_sub_events = super_event['subEvents']
                    new_sub_events.remove(sub_event)
                    # set all events except for the current event
                    update_one(current_app.config['EVENT_COLLECTION'],
                               condition={"_id": ObjectId(super_event['_id'])},
                               update={"$set": {"subEvents": new_sub_events}})

                    if get_user_event_status(super_event['_id']) == "approved":
                        success = put_user_event(super_event['_id'])
                        if not success:
                            __logger.error("updating super event in building block failed")

    delete_user_event(id)

    if len(glob(path.join(Config.WEBTOOL_IMAGE_MOUNT_POINT, id + '*'))) > 0:
        try:
            remove(glob(path.join(Config.WEBTOOL_IMAGE_MOUNT_POINT, id + '*'))[0])
        except OSError:
            __logger.error("delete event:{} image failed".format(id))
    record = find_one(Config.IMAGE_COLLECTION, condition={"eventId": id})
    if record:
        success = s3_image_delete(id, userEvent.get("platformEventId"), record.get("_id"))
        if success:
            __logger.info("{}, s3: s3_image_delete()".format(record.get('status')))
            updateResult = update_one(current_app.config['IMAGE_COLLECTION'],
                                      condition={'eventId': id},
                                      update={"$set": {'status': 'deleted',
                                                       'eventId': id}}, upsert=True)
            if updateResult.modified_count == 0 and updateResult.matched_count == 0 and updateResult.upserted_id is None:
                __logger.error("Failed to mark image record as deleted of event: {} in the deletion of event".format(id))
        else:
            __logger.error("deleting image for event:{} failed in event deletion".format(id))
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
def searchsub2():
    if request.method == "GET":
       search_term = request.values.get("data")
       results = group_subevents_search(search_term, get_admin_group_ids())
       return jsonify(results)
    else:
       return jsonify([]), 200

@userbp.route('/searchsub/<id>', methods=['GET'])
@role_required('user')
def searchsub(id):
    if request.method == "GET":
       search_term = request.values.get("data")
       results = group_subevents_search(search_term, get_admin_group_ids())
       for result in results:
           if result['eventid'] == id:
               results.remove(result)
       return jsonify(results)
    else:
       return jsonify([]), 200

@userbp.route('/event/<id>/image', methods=['GET'])
@role_required("user")
def view_image(id):
    record = find_one(Config.IMAGE_COLLECTION, condition={"eventId": id})
    event = find_user_event(id)
    if record:
        success = s3_image_download(id, event.get("platformEventId"), record.get("_id"))
        if success:
            try:
                __logger.info("{}, s3: s3_image_download()".format(record.get('status')))
                path_to_tmp_image = os.path.join(os.getcwd(), 'temp', id + ".jpg")

                def get_image():
                    with open(path_to_tmp_image, 'rb') as f:
                        yield from f
                    os.remove(path_to_tmp_image)

                response = current_app.response_class(get_image(), mimetype='image/jpg')
                return response
            except Exception as ex:
                __logger.exception(ex)
                __logger.error("returning image for event:{} on s3 to user failed".format(id))
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
def sub_event_platform(platformEventId):
    try:
        eventId = clickable_utility(platformEventId)
        return redirect(url_for('user_events.user_an_event', id=eventId))

    except Exception as ex:
        __logger.exception(ex)
        __logger.error("Redirect for platformEventId {} failed".format(platformEventId))
        abort(500)

@userbp.route('/event/platform/<eventId>',  methods=['GET'])
@role_required("user")
def sub_event(eventId):
    try:
        return redirect(url_for('user_events.user_an_event', id=eventId))

    except Exception as ex:
        __logger.exception(ex)
        __logger.error("Redirect for eventid {} failed".format(eventId))
        abort(500)
