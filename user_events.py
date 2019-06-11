from flask import Flask,render_template,url_for,flash, redirect, Blueprint, request
from .utilities.user_utilities import *
from .utilities.constants import *

userbp = Blueprint('user_events', __name__, url_prefix='/user-events')

@userbp.route('/', methods=['GET', 'POST'])
def user_events():
    if request.method == 'POST':
		#format : 'id=1234' /'type=Academic'/'id=1234&type=Academic'
        searchInput = request.form['searchInput']
        search_id = None
        search_type = None
        if '&' in searchInput:
        	input_list = searchInput.split('&')
        	if len(input_list[0]) > 3 and input_list[0][0:2]=='id':
        		search_id = input_list[0][3:]
        	if len(input_list[1]) > 5 and input_list[1][0:4]=='type':
        		search_type = input_list[1][5:]
        else:
        	if len(searchInput) > 3 and searchInput[0:2]=='id':
        		search_id = searchInput[3:]
        	elif len(searchInput) > 5 and searchInput[0:4]=='type':
        		search_type = searchInput[5:]
        result_dic = {}
        if search_id != None:
        	result_dic['eventId'] = search_id
        if search_type != None:
        	result_dic['eventType'] = search_type
        #print(result_dic)
        posts = get_searched_user_events(result_dic)
    else:
        posts = get_all_user_events()
    return render_template("events/user-events.html", posts=posts)

@userbp.route('/event<id>',  methods=['GET'])
def user_an_event(id):
    post = find_user_event(id)
    return render_template("events/event.html", post = post)

@userbp.route('/event<id>/edit', methods=['GET', 'POST'])
def user_an_event_edit(id):
    post_by_id = find_user_event(id)
    if request.method == 'POST':
        # change the specific event
        post_by_id['titleURL'] = request.form['titleURL']
        post_by_id['startDate'] = request.form['startDate']
        post_by_id['endDate'] = request.form['endDate']
        post_by_id['cost'] = request.form['cost']
        post_by_id['sponsor'] = request.form['sponsor']
        # more parts editable TODO ....

        # insert update_user_event function here later
        update_user_event(id, post_by_id)
    return render_template("events/event-edit.html", post = post_by_id, eventTypeMap = eventTypeMap)

@userbp.route('/event<id>/approve')
def user_an_event_approve(id):
    update_user_event(id, {"eventStatus": "approve"})
    return redirect(url_for("user_events.user_an_event", id=id))
