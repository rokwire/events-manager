import json
import datetime

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, current_app, session
)
from werkzeug.exceptions import abort

from .auth import login_required

from .utilities.source_utilities import *
from .utilities.sourceEvents import start
from .utilities.constants import eventTypeMap
from flask_paginate import Pagination, get_page_args

from datetime import datetime

bp = Blueprint('event', __name__, url_prefix='/event')

@bp.route('/source/<sourceId>')
def source(sourceId):
    # page = request.args.get('page', 0, type=int)
    allsources = current_app.config['INT2SRC']
    title = allsources[sourceId][0]
    calendars = allsources[sourceId][1]
    return render_template('events/source-events.html', allsources=allsources, sourceId=sourceId, title=title, calendars=calendars, total=0)

@bp.route('/calendar/<calendarId>')
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
    return render_template('events/calendar.html', title=title, source=(sourceId, sourcetitle), posts=events, calendarId=calendarId,
                            select_status=select_status, calendarStatus=calendarStatus,
                            page=page, per_page=per_page, pagination=pagination, isUser=False)

@bp.route('/search')
@login_required
def search():
   return render_template('events/search.html', sources=current_app.config['INT2SRC'])

@bp.route('/setting', methods=('GET', 'POST'))
@login_required
def setting():
    if request.method == 'POST':
        print(request.form)
        allstatus = get_all_calendar_status()
        update_calendars_status(request.form, allstatus)
    allstatus = get_all_calendar_status()
    return render_template('events/setting.html', sources=current_app.config['INT2SRC'], allstatus=allstatus)


@bp.route('/download', methods=['POST'])
@login_required
def download():
    targets = request.get_json()
    if targets:
       start(targets)
    return json.dumps({'status': 'OK', 'data': 'complete'})

@bp.route('/<calendarId>/select', methods=['POST'])
@login_required
def select(calendarId):
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
@login_required
def approveCalendar():
    calendarId = request.form['calendarId']
    approve_calendar_db(calendarId)
    return "success", 200

@bp.route('/disapprove', methods=('GET', 'POST'))
@login_required
def disapproveCalendar():
    calendarId = request.form['calendarId']
    disapprove_calendar_db(calendarId)
    return "success", 200

@bp.route("/source/<id>/approve")
@login_required
def approveEvent(id):
    approve_event(id)
    return redirect(url_for("event.detail", eventId=id))

@bp.route("/source/<id>/disapprove")
@login_required
def disapproveEvent(id):
    disapprove_event(id)
    return redirect(url_for("event.detail", eventId=id))

@bp.route('/detail/<eventId>')
def detail(eventId):
    event = get_event(eventId)
    # print("event: {}".format(event))
    source = current_app.config['INT2SRC'][event['sourceId']]
    sourceName = source[0]
    calendarName = ''
    for dict in source[1]:
        if event['calendarId'] in dict:
            calendarName = dict[event['calendarId']]
    return render_template("events/event.html", post=event, isUser=False, sourceName=sourceName, calendarName=calendarName, 
                            eventTypeMap = eventTypeMap, apiKey=current_app.config['GOOGLE_MAP_VIEW_KEY'])


@bp.route('/edit/<eventId>', methods=('GET', 'POST'))
def edit(eventId):
    post_by_id = get_event(eventId)
    # create dic for eventType values - new category
    eventTypeValues = {}
    for key in eventTypeMap:
        value = eventTypeMap[key]
        eventTypeValues[value] = 0
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
    return render_template("events/event-edit.html", post = post_by_id, eventTypeMap = eventTypeMap, eventTypeValues=eventTypeValues, isUser=False, sourceName=sourceName, calendarName=calendarName)

@bp.route('/schedule', methods=('GET', 'POST'))
def schedule():
    time = request.form['time']
    present = datetime.now()
    d = present.strftime('%Y-%m-%d-')
    time = datetime.strptime("{}{}".format(d, time), '%Y-%m-%d-%H:%M')
    if time < present:
        time = present
        print("incorrect time")
    # scheduler function
    print(time)
    return "success", 200
