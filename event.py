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

import json
import datetime

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, current_app, session, Request, jsonify
)
from werkzeug.exceptions import abort

from .auth import role_required

from .scheduler import scheduler_add_job
from .utilities.source_utilities import *
from .utilities.sourceEvents import start
from .utilities.constants import eventTypeMap, eventTypeValues
from flask_paginate import Pagination, get_page_args

from datetime import datetime
from .config import Config


bp = Blueprint('event', __name__, url_prefix=Config.URL_PREFIX+'/event')

@bp.route('/source/<sourceId>')
@role_required("source")
def source(sourceId):
    allsources = current_app.config['INT2SRC']
    title = allsources[sourceId][0]
    calendars = allsources[sourceId][1]
    return render_template('events/source-events.html', 
                            allsources=allsources, sourceId=sourceId, 
                            title=title, calendars=calendars, total=0, 
                            eventTypeValues=eventTypeValues, isUser=False)

@bp.route('/calendar/<calendarId>')
@role_required("source")
def calendar(calendarId):
    if 'select_status' in session:
        select_status = session['select_status']
    else:
        select_status = ['pending']
        session['select_status'] = select_status
    # find source of current calendar
    sourceId = '0'
    sourcetitle = "error: None"
    title = ""
    for key, source in current_app.config['INT2SRC'].items():
        for item in source[1]:
            if calendarId in item:
                title = item[calendarId]
                sourceId = key
                sourcetitle = source[0]

    try:
        page, per_page, offset = get_page_args(page_parameter='page', per_page_parameter='per_page')
    except ValueError:
        page = 1
    per_page = current_app.config['PER_PAGE']
    offset = (page - 1) * per_page
    total = get_calendar_events_count(sourceId, calendarId, select_status)
    if offset >= total or page <= 0:
        page = 1
        offset = 0
    events = get_calendar_events_pagination(sourceId, calendarId, select_status, offset, per_page)
    pagination = Pagination(page=page, per_page=per_page, total=total, css_framework='bootstrap4')
    print("sourceId: {}, calendarId: {}, number of events: {}".format(sourceId, calendarId, len(list(events))))

    calendarStatus = get_calendar_status(calendarId)
    return render_template('events/calendar.html', 
                            title=title, source=(sourceId, sourcetitle), 
                            posts=events, calendarId=calendarId,isUser=False,
                            select_status=select_status, calendarStatus=calendarStatus,
                            pagination=pagination, eventTypeValues=eventTypeValues)

@bp.route('/setting', methods=('GET', 'POST'))
@role_required("source")
def setting():
    if request.method == 'POST':
        print(request.form)
        #add update calendars
        allstatus = get_all_calendar_status()
        update_calendars_status(request.form, allstatus)
    calendar_in_db = get_all_calendar_status()
    calendar_ids = calendar_in_db.keys()
    calendar_source = list()
    calendar_status = dict()
    for calendar_id in calendar_ids:
        calendar_source.append({calendar_id: calendar_in_db.get(calendar_id).get('calendarName')})
        calendar_status[calendar_id] = calendar_in_db.get(calendar_id).get('status')
    INT2SRC = {
        '0': ('WebTools', calendar_source),
        '1': ('EMS', []),
    }
    calendar_prefix=current_app.config['WEBTOOL_CALENDAR_LINK_PREFIX']
    return render_template('events/setting.html', 
                            isUser=False,
                            sources=INT2SRC, 
                            allstatus=calendar_status, 
                            url_prefix=calendar_prefix)

@bp.route('/download', methods=['POST'])
@role_required("source")
def download():
    targets = request.get_json()
    if targets:
        start(targets)
    return json.dumps({'status': 'OK', 'data': 'complete'})

@bp.route('/select', methods=['POST'])
@role_required("source")
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

@bp.route('/approve', methods=('GET', 'POST'))
@role_required("source")
def approveCalendar():
    calendarId = request.form['calendarId']
    approve_calendar_db(calendarId)
    return "success", 200

@bp.route('/disapprove', methods=('GET', 'POST'))
@role_required("source")
def disapproveCalendar():
    calendarId = request.form['calendarId']
    disapprove_calendar_db(calendarId)
    return "success", 200

@bp.route("/approveEvent/<id>", methods=['GET', 'POST'])
@role_required("source")
def approveEvent(id):
    approve_event(id)
    return "success", 200

@bp.route("/disapproveEvent/<id>", methods=['GET', 'POST'])
@role_required("source")
def disapproveEvent(id):
    disapprove_event(id)
    return "success", 200

@bp.route('/detail/<eventId>')
@role_required("source")
def detail(eventId):
    event = get_event(eventId)
    source = current_app.config['INT2SRC'][event['sourceId']]
    sourceName = source[0]
    calendarName = ''
    for dict in source[1]:
        if event['calendarId'] in dict:
            calendarName = dict[event['calendarId']]
    return render_template("events/event.html", 
                            post=event, isUser=False, sourceName=sourceName, calendarName=calendarName,
                            eventTypeMap = eventTypeMap, apiKey=current_app.config['GOOGLE_MAP_VIEW_KEY'])


@bp.route('/edit/<eventId>', methods=('GET', 'POST'))
@role_required("source")
def edit(eventId):
    post_by_id = get_event(eventId)
    if request.method == 'POST':
        # change the specific event
        post_by_id['titleURL'] = request.form['titleURL']
        post_by_id['startDate'] = request.form['startDate']
        post_by_id['endDate'] = request.form['endDate']
        post_by_id['cost'] = request.form['cost']
        post_by_id['sponsor'] = request.form['sponsor']
        # more parts editable TODO ....

        # insert update_user_event function here later
        update_event(eventId, post_by_id)

    source = current_app.config['INT2SRC'][post_by_id['sourceId']]
    sourceName = source[0]
    calendarName = ''
    for dict in source[1]:
        if post_by_id['calendarId'] in dict:
            calendarName = dict[post_by_id['calendarId']]
    return render_template("events/event-edit.html", 
                            post = post_by_id, eventTypeMap = eventTypeMap, 
                            eventTypeValues=eventTypeValues, isUser=False, 
                            sourceName=sourceName, calendarName=calendarName)

@bp.route('/searchresult', methods=['GET'])
@role_required("source")
def searchresult():
    if 'select_status' in session:
        select_status = session['select_status']
    else:
        select_status = ['pending']
        session['select_status'] = select_status

    condition = {}
    eventId = request.args.get('form-eventId', None)
    if eventId:
        condition['eventId'] = eventId
    category = request.args.get('category', None)
    if category:
        condition['category'] = category

    print(eventId, category)
    try:
        page, per_page, offset = get_page_args(page_parameter='page', per_page_parameter='per_page')
    except ValueError:
        page = 1
    per_page = current_app.config['PER_PAGE']
    offset = (page - 1) * per_page

    total = get_search_events_count(condition, select_status)
    if offset >= total or page < 1:
        page = 1
        offset = 0
    pagination = Pagination(page=page, per_page=per_page, total=total, css_framework='bootstrap4')
    events = get_search_events(condition, select_status, offset, per_page)
    source = request.args.get('source')
    id = request.args.get('id')
    print("{},{},{}".format(page, per_page, offset))
    return render_template("events/searchresult.html", 
                            eventTypeValues=eventTypeValues, source=source, id=id, 
                            eventId=eventId, category=category, isUser=False,
                            posts=events, pagination=pagination, select_status=select_status
    )

@bp.route('/schedule', methods=['POST'])
@role_required("source")
def schedule():
    time = request.form.get('time')
    targets = json.loads(request.form.get('targets'))
    present = datetime.now()
    d = present.strftime('%Y-%m-%d-')
    time = datetime.strptime("{}{}".format(d, time), '%Y-%m-%d-%H:%M')
    if time < present:
        time = present
        print("incorrect time")
        return redirect('event.setting')
    # scheduler function
    print(time)
    scheduler_add_job(current_app._get_current_object(), current_app.scheduler, start, time, targets=targets)
    return "success", 200


@bp.route('/add-new-calendar', methods=['POST'])
@role_required("source")
def add_new_calendar():
    print(request.form)
    # new calendars
    calendarID = request.form.get('data[calendarID]')
    calendarName = request.form.get('data[calendarName]')
    print(calendarID)
    print(calendarName)
    if calendarID == '' or calendarName == '':
        print("should have both ID and Name!")
        return "invalid", 200
    # all newly added calendar will be default to "disapproved"
    calendar_document = {"calendarId" : calendarID, "calendarName": calendarName, "status": "disapproved"}
    insert_result = insert_one(current_app.config['CALENDAR_COLLECTION'], document = calendar_document)
    # insert error condition check
    if insert_result.inserted_id is None:
        print("Insert calendar " + calendarID +" failed")
        return redirect('event.setting')
        return "fail", 400
    else:
        print(current_app.config['INT2CAL'])
        print("successfully inserted calendar "+ calendarID)
        return "success", 200

@bp.route('/search', methods=['GET', 'POST'])
@role_required('source')
def search():
    # TODO: waiting to fulfill backend functionality
    if request.method == "GET":
        return jsonify(["test1", "test2", "test3", "test4", "test5"])
    return jsonify([]), 200
