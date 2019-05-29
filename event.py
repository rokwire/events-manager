from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

import request
import sys
import flaskr.constants

bp = Blueprint('event', __name__, url_prefix='/event')

@bp.route('/source/<sourceId>', methods=('GET', 'POST'))
#@login_required
def source(sourceId):
  page = request.args.get('page', 1, type=int)
  start = (page-1)*current_app.config['PAGINATION']
  allsources = flaskr.constants.int2SrcDB
  title = allsources[sourceId][0]
  calendars = allsources[sourceId][1][start:start+current_app.config['PAGINATION']]
  total = math.ceil(len(calendars)/current_app.config['PAGINATION'])
  next_page = url_for('event.source', sourceId=sourceId, page=page+1)) if len(calendars) > current_app.config['PAGINATION'] else None
  prev_page = url_for('event.source', sourceId=sourceId, page=page-1)) if page > 1 else None
  return render_template('events/sources.html', allsources=allsources, sourceId=sourceId, title=title, calendars=calendars, current_page=page, next_page=next_page, prev_page=prev_page, total=total)

@bp.route('calendar/<calendarId>', methods=('GET', 'POST'))
 @login_required
def calendar(calendar_id):
  events = db.findEventInCalendar(calendar_id)
  title = "NCSA"
  return render_template('events/calendar.html', events=list(events), title=title)

@bp.route('/approve/<eventid>', methods=('GET', 'POST'))
@login_required
def approve(eventid):
  r = mongo.db.rawevents.find_one_and_update({"_id": ObjectId(eventid)}, {"$set": {"status":"approved"}})
  return "success", 200
