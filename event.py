from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, current_app
)
from werkzeug.exceptions import abort

from .auth import login_required
from .db import find_all, find_one_and_update

import sys
from .utilities.constants import int2SrcDB
import math

from bson.objectid import ObjectId

bp = Blueprint('event', __name__, url_prefix='/event')

@bp.route('/source/<sourceId>', methods=('GET', 'POST'))
@login_required
def source(sourceId):
    page = request.args.get('page', 0, type=int)
    allsources = int2SrcDB
    #print(allsources, file=sys.stderr)
    title = allsources[sourceId][0]
    ### pagination
    # start = page*current_app.config['PAGINATION']
    # calendarstotalnum = len(allsources[sourceId][1])
    # end = start + current_app.config['PAGINATION']
    # endflag = False
    # if end >= calendarstotalnum:
    #     end = calendarstotalnum
    # else:
    #     endflag = True
    # calendars = allsources[sourceId][1][start:end]
    # total = math.ceil(calendarstotalnum/current_app.config['PAGINATION'])
    # next_page = url_for('event.source', sourceId=sourceId, page=page+1) if endflag else None
    # prev_page = url_for('event.source', sourceId=sourceId, page=page-1) if page > 0 else None
#    return render_template('events/source-events.html', allsources=allsources, sourceId=sourceId, title=title, calendars=calendars, current_page=page, next_page=next_page, prev_page=prev_page, total=total)

    calendars = allsources[sourceId][1]
    return render_template('events/source-events.html', allsources=allsources, sourceId=sourceId, title=title, calendars=calendars, total=0)

@bp.route('calendar/<calendarId>', methods=('GET', 'POST'))
@login_required
def calendar(calendarId):
    # find source of current calendar
    sourceId = 0
    sourcetitle = "error: None"
    title = ""
    for key, source in int2SrcDB.items():
        for item in source[1]:
            if calendarId in item:
                title = item[calendarId]
                sourceId = key
                sourcetitle = source[0]

    events = list(find_all("rawevents"))
    #print(events, file=sys.stderr)
    return render_template('events/calendar.html', title=title, source=(sourceId, sourcetitle), posts=events, total=0)

# @bp.route('/approveCalendar/<calendarId>', methods=('GET', 'POST'))
# @login_required
# def approveCalendar(calendarId):
#     find_one_and_update("calendar", {"_id": ObjectId(calendarId)}, {"$set": {"status": "approved"}})
#     return "success", 200
