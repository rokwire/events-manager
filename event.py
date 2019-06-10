from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, current_app
)
from werkzeug.exceptions import abort

from .auth import login_required
from .db import find_all

from .utilities.constants import int2SrcDB

bp = Blueprint('event', __name__, url_prefix='/event')

@bp.route('/source/<sourceId>')
@login_required
def source(sourceId):
    # page = request.args.get('page', 0, type=int)
    allsources = int2SrcDB
    title = allsources[sourceId][0]
    calendars = allsources[sourceId][1]
    return render_template('events/source-events.html', allsources=allsources, sourceId=sourceId, title=title, calendars=calendars, total=0)

@bp.route('/calendar/<calendarId>')
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
    return render_template('events/calendar.html', title=title, source=(sourceId, sourcetitle), posts=events, total=0)

@bp.route('/setting')
@login_required
def setting():
    return render_template('events/setting.html', sources=int2SrcDB)
