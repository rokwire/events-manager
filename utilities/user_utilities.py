from flask import current_app
from bson.objectid import ObjectId
from bson.errors import InvalidId

from ..db import find_all, find_one, update_one, find_distinct, insert_one

def get_all_user_events(select_status):

    eventIds = find_distinct(current_app.config['EVENT_COLLECTION'], key="eventId",
                             condition={"sourceId": {"$exists": False},
                                        "eventStatus": {"$in": select_status}})
    events_by_eventId = {}
    for eventId in eventIds:
        events = list(find_all(current_app.config['EVENT_COLLECTION'],
                               filter={"eventId": eventId,
                                       "eventStatus": {"$in": select_status}}))

        if events:
            events_by_eventId[eventId] = events

    return events_by_eventId

    # return find_all(current_app.config['EVENT_COLLECTION'], filter={"sourceId": {"$exists": False},
    #                                                                 "eventStatus": {"$in": select_status}})

def get_all_user_events_count(select_status):

    return len(find_distinct(current_app.config['EVENT_COLLECTION'], key="eventId",
                             condition={"sourceId": {"$exists": False},
                                        "eventStatus": {"$in": select_status}}))


def get_all_user_events_pagination(select_status, skip, limit):

    eventIds = find_distinct(current_app.config['EVENT_COLLECTION'], key="eventId",
                             condition={"sourceId": {"$exists": False},
                                        "eventStatus": {"$in": select_status}},
                             skip=skip,
                             limit=limit)
    begin = skip
    end = min(len(eventIds), skip+limit)
    events_by_eventId = {}
    for eventId in eventIds[begin:end]:
        events = list(find_all(current_app.config['EVENT_COLLECTION'],
                               filter={"eventId": eventId,
                                       "eventStatus": {"$in": select_status}}))
        if events:
            events_by_eventId[eventId] = events

    return events_by_eventId


# TODO get searched posts
def get_searched_user_events(searchDic, select_status):

    searchDic['sourceId'] = {"$exists": False}
    searchDic['eventStatus'] = {"$in": select_status}
    return list(find_all(current_app.config['EVENT_COLLECTION'], filter=searchDic))

def find_user_event(objectId):
    try:
        _id = ObjectId(objectId)
    except InvalidId:
        return {}
    return find_one(current_app.config['EVENT_COLLECTION'], condition={"_id": ObjectId(objectId)})


def update_user_event(objectId, update, delete_field=None):
    try:
        _id = ObjectId(objectId)
    except InvalidId:
        return {}
    updateResult = update_one(current_app.config['EVENT_COLLECTION'], condition={"_id": ObjectId(objectId)},
                              update={
                                  "$set": update
                              })
    if delete_field:
        updateResult = update_one(current_app.config['EVENT_COLLECTION'], condition={"_id": ObjectId(objectId)},
                                  update={
                                      "$unset": delete_field
                                  })

    if updateResult.modified_count == 0 and updateResult.matched_count == 0 and updateResult.upserted_id is None:
        print("Update {} fails in update_user_event".format(objectId))

def find_user_all_object_events(eventId):
    print(eventId)
    result_events =  find_all(current_app.config['EVENT_COLLECTION'], filter={"eventId": eventId})
    if result_events is None:
        return []
    return result_events

def delete_user_event(eventId):
    pass

# Find the approval status for one event
def get_user_event_status(objectId):
    pass

def approve_user_event(objectId):
    pass

def disapprove_user_event(objectId):
    pass

def create_new_user_event(new_user_event):
    update_result = None
    result = insert_one(current_app.config['EVENT_COLLECTION'], new_user_event)
    if result.inserted_id:
        update = dict()
        update['eventStatus'] = 'pending'
        update['eventId'] = result.inserted_id
        # for key in update:
        update_result = update_one(current_app.config['EVENT_COLLECTION'],
                                   condition={"_id": ObjectId(result.inserted_id)},
                                   update={
                                      "$set": update
                                  })
    if update_result is None or update_result.modified_count == 0 and update_result.matched_count == 0 and update_result.upserted_id is None:
        print("create_new_user_event {} failed")
    return result.inserted_id

def populate_event_from_form(post_form):
    new_event = dict()
    super_event = False
    for item in post_form:
        if item !='firstName' and item != 'lastName' and item != 'email' and item != 'phone' and item != 'organization' and item != "id" and item != 'track' and item != 'isFeatured':
            new_event[item] = post_form.get(item)
            print("item:", item)
            print("new event item:", new_event[item])
        if item == 'isSuperEvent':
            if post_form.get(item) == 'on':
                new_event['isSuperEvent'] = True
                super_event = True
    if super_event == False:
        new_event['isSuperEvent'] = False

    new_event['contacts'] = get_contact_list (post_form)

    new_event['subevent'] = get_subevent_list (post_form)

    return new_event

def get_contact_list (post_form):

    contacts_arrays = []
    has_contacts_in_request = False
    for item in post_form:
        # when contact input field is not empty
        if item == 'firstName' or item == 'lastName' or item == 'email' or item == 'phone' or item == 'organization':
            contact_list = post_form.getlist(item)
            if len(contact_list) != 0:
                # delete first group of empty string
                contact_list = contact_list[1:]
                contacts_arrays += [contact_list]
        # new_event[item] = post_form.get(item)

    if contacts_arrays:
        num_of_contacts = len(contacts_arrays[0])
        contacts_dic = []
        for i in range(num_of_contacts):
            a_contact = {}
            firstName = contacts_arrays[0][i]
            lastName = contacts_arrays[1][i]
            email = contacts_arrays[2][i]
            phone = contacts_arrays[3][i]
            orginazation = contacts_arrays[4][i]
            if firstName != "":
                 a_contact['firstName'] = firstName
            if lastName != "":
                 a_contact['lastName'] = lastName
            if email != "":
                 a_contact['email'] = email
            if phone != "":
                a_contact['phone'] = phone
            if orginazation != "":
                a_contact['organization'] = orginazation
            if a_contact != {}:
                contacts_dic.append(a_contact)
        if contacts_dic != []:
            has_contacts_in_request = True
            return contacts_dic
        # return ""


#helper function to get subevent
def get_subevent_list (post_form):
    subevent_arrays = []
    for item in post_form:
        if item == 'id' or item == 'track' or item == 'isFeatured':
            sub_list = post_form.getlist(item)
            if len(sub_list) != 0:
                sub_list = sub_list[1:]
                subevent_arrays += [sub_list]
    if subevent_arrays:
        num_of_sub = len(subevent_arrays[0])
        subevent_dict = []
        for i in range(num_of_sub):
            a_subevent = {}
            sub_id = subevent_arrays[0][i]
            sub_track = subevent_arrays[1][i]
            sub_feature = subevent_arrays[2][i]
            if sub_id != "":
                a_subevent['id'] = sub_id
            if sub_track != "":
                a_subevent['track'] = sub_track
            if sub_feature != "":
                if sub_feature == 'Featured':
                    a_subevent['isFeatured'] = True
                else:
                    a_subevent['isFeatured'] = False

            if a_subevent != {}:
                subevent_dict.append(a_subevent)
        if subevent_dict != []:
            return subevent_dict