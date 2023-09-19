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

import pymongo
import traceback
from pymongo.errors import PyMongoError, ServerSelectionTimeoutError
from pymongo.results import InsertOneResult, UpdateResult
from pymongo.mongo_client import MongoClient
from flask import current_app,g
from .config import Config
import logging
from time import gmtime

logging.Formatter.converter = gmtime
logging.basicConfig(level=logging.INFO, datefmt='%Y-%m-%dT%H:%M:%S',
                    format='%(asctime)-15s.%(msecs)03dZ %(levelname)-7s [%(threadName)-10s] : %(name)s - %(message)s')
__logger = logging.getLogger("db.py")

######################################################################
### Basic DB creation and access functions
######################################################################
def get_db():
    if 'dbclient' not in g:
        if current_app.config['DBTYPE'] == 'mongoDB':
            try:
                g.dbclient = pymongo.MongoClient(current_app.config['MONGO_URL'])
                g.db = g.dbclient.get_database(name=current_app.config['MONGO_DATABASE'])
            except PyMongoError:
                __logger.error("MongoDB connection failed.")
                if 'dbclient' in g:
                    g.pop('dbclient', None)
                return None
            except Exception as ex:
                __logger.error(str(ex))
    return g.db


def close_db(e=None):
    if current_app.config['DBTYPE'] == 'mongoDB':
        g.pop('db', None)
        dbclient = g.pop('dbclient', None)
        if dbclient is not None:
            dbclient.close()


def init_db(app):
    app.teardown_appcontext(close_db)

    # Set up Mongo client for text indexing
    global client
    client = MongoClient(Config.MONGO_URL)
    db = client.get_database('rokwire')
    events = db['eventsmanager_events']
    events.create_index([("title", pymongo.TEXT)])


######################################################################
### Basic DB query and insert functions
######################################################################
def find_one(co_or_ta, condition=None, *args, **kwargs):
    db = get_db()
    dbType = current_app.config['DBTYPE']
    if co_or_ta is None or db is None:
        return {}

    if dbType == "mongoDB":
        try:
            collection = db.get_collection(co_or_ta)
            result = collection.find_one(filter=condition, *args, **kwargs)
            if not result:
                return {}
            return result
        except TypeError:
            __logger.error("Invalid arguments inserted using find_one")
            return {}
        except Exception as ex:
            __logger.exception(ex)
            return {}


def find_one_and_update(co_or_ta, condition=None, update=None, **kwargs):
    db = get_db()
    dbType = current_app.config['DBTYPE']

    if co_or_ta is None or condition is None or update is None or db is None:
        return {}

    if dbType == "mongoDB":
        try:
            collection = db.get_collection(co_or_ta)
            result = collection.find_one_and_update(condition, update, **kwargs)
            if not result:
                __logger.error("No matching record found in MongoDB")
                return {}
            return result
        except TypeError:
            __logger.error("Invalid arguments inserted using find_one_and_update")
            return {}
        except Exception as ex:
            __logger.exception(ex)
            return {}


def find_all(co_or_ta, **kwarg):
    db = get_db()
    dbType = current_app.config['DBTYPE']

    if co_or_ta is None or db is None:
        return []

    if dbType == "mongoDB":
        try:
            collection = db.get_collection(co_or_ta)
            result = collection.find(**kwarg)
            if not result:
                return []
            return list(result)
        except TypeError:
            __logger.error("Invalid arguments inserted using find_all")
            return []
        except Exception as ex:
            __logger.exception(ex)
            return []

def find_all_previous_event_ids(co_or_ta, filter, **kwarg):
    db = get_db()
    dbType = current_app.config['DBTYPE']
    if co_or_ta is None or db is None:
        return []

    if dbType == "mongoDB":
        try:
            collection = db.get_collection(co_or_ta)
            projection = {'_id':1,'dataSourceEventId':1}
            result = collection.find(filter=filter, projection=projection, **kwarg)
            if not result:
                return []

            ids_object_list = list()
            for data_pair in result:
                ids_object_list.append(data_pair)
            return ids_object_list

        except TypeError:
            __logger.error("Invalid arguments inserted using find_all_event_ids")
            return []
        except Exception as ex:
            __logger.exception(ex)
            return []


def find_all_event_ids(co_or_ta, **kwarg):
    db = get_db()
    dbType = current_app.config['DBTYPE']

    if co_or_ta is None or db is None:
        return []

    if dbType == "mongoDB":
        try:
            collection = db.get_collection(co_or_ta)
            projection = {'_id':0,'dataSourceEventId':1}
            result = collection.find(projection=projection, **kwarg)
            if not result:
                return []
            id_object_list = list(result)
            eventId_list = []
            for ele in id_object_list:
                eventId_list += [ele['dataSourceEventId']]
            return eventId_list

        except TypeError:
            return []
        except Exception as ex:
            __logger.exception(ex)
            return []


def insert_one(co_or_ta, document=None, **kwargs):
    db = get_db()
    dbType = current_app.config['DBTYPE']

    if document is None or co_or_ta is None or db is None:
        return InsertOneResult()

    if dbType == "mongoDB":
        try:
            collection = db.get_collection(co_or_ta)
            result = collection.insert_one(document=document, **kwargs)
            if not result:
                return InsertOneResult()
            return result
        except Exception as ex:
            __logger.exception(ex)
            return InsertOneResult()


def update_one(co_or_ta, condition=None, update=None, **kwargs):
    db = get_db()
    dbType = current_app.config['DBTYPE']

    if update is None or co_or_ta is None or condition is None or db is None:
        return UpdateResult()

    if dbType == "mongoDB":
        try:
            collection = db.get_collection(co_or_ta)
            result = collection.update_one(condition, update, **kwargs)
            if not result:
                return UpdateResult()
            return result
        except Exception as ex:
            __logger.exception(ex)
            return UpdateResult()

def update_many(co_or_ta, condition=None, update=None, **kwargs):
    db = get_db()
    dbType = current_app.config['DBTYPE']

    if update is None or co_or_ta is None or condition is None or db is None:
        return UpdateResult()

    if dbType == "mongoDB":
        try:
            collection = db.get_collection(co_or_ta)
            result = collection.update_many(condition, update, **kwargs)
            if not result:
                return UpdateResult()
            return result
        except Exception as ex:
            __logger.exception(ex)
            return UpdateResult()

def replace_one(co_or_ta, condition=None, replacement=None, **kwargs):
    db = get_db()
    dbType = current_app.config['DBTYPE']

    if co_or_ta is None or condition is None or replacement is None or db is None:
        return UpdateResult()

    if dbType == "mongoDB":
        try:
            collection = db.get_collection(co_or_ta)
            result = collection.replace_one(condition, replacement, **kwargs)
            if not result:
                return UpdateResult()
            return result
        except Exception as ex:
            __logger.exception(ex)
            return UpdateResult()

def find_distinct(co_or_ta, key=None, condition=None, **kwargs):
    db = get_db()
    dbType = current_app.config['DBTYPE']

    if key is None or co_or_ta is None:
        return []

    if dbType == "mongoDB":
        try:
            collection = db.get_collection(co_or_ta)
            result = collection.distinct(key, filter=condition)
            if not result:
                return []
            return list(result)
        except Exception as ex:
            __logger.exception(ex)
            return []

def get_count(co_or_ta, filter, **kwargs):
    db = get_db()
    dbType = current_app.config['DBTYPE']

    if co_or_ta is None:
        return 0

    if dbType == "mongoDB":
        try:
            collection = db.get_collection(co_or_ta)
            result = collection.count_documents(filter, **kwargs)
            if not result:
                return 0
            return result
        except Exception as ex:
            __logger.exception(ex)
            return 0

# Parameters: collection name, *objectId* list to delete
def delete_events_in_list(co_or_ta, objectId_list_to_delete, **kwargs):
    db = get_db()
    dbType = current_app.config['DBTYPE']

    if co_or_ta is None or db is None:
        return []

    if dbType == "mongoDB":
        try:
            collection = db.get_collection(co_or_ta)
            query = {'_id':{'$in': objectId_list_to_delete}}
            result = collection.remove(query)
            if not result:
                return []
            return objectId_list_to_delete

        except TypeError:
            return []
        except Exception:
            return []

# Parameters: collection name, string to look for
def text_index_search(co_or_ta, search_string, **kwargs):
    db = get_db()
    dbType = current_app.config['DBTYPE']

    if search_string is None or co_or_ta is None:
        return []

    if dbType == "mongoDB":
        try:
            collection = db.get_collection(co_or_ta)
            # Will return all records with matching regex and is case insensitive for title search
            # There is also a projection limiting the fields returned to only title and platformEventID
            result = collection.find({"$text": {"$search": search_string}, "eventStatus": "approved"}, {"title": 1, "platformEventId": 1, "category": 1, "startDate": 1, "_id": 0})
            if not result:
                return []
            return result

        except Exception:
            return []

def group_text_index_search(co_or_ta, search_string, admin_group_ids):
    db = get_db()
    dbType = current_app.config['DBTYPE']

    if search_string is None or co_or_ta is None:
        return []

    if dbType == "mongoDB":
        try:
            collection = db.get_collection(co_or_ta)
            # Will return all records with matching regex and is case insensitive for title search
            # There is also a projection limiting the fields returned to only title and platformEventID
            result = collection.find({"$text": {"$search": search_string}, "sourceId": {"$exists": False}, "createdByGroupId":{"$in": admin_group_ids}},
                                     {"title": 1, "platformEventId": 1, "category": 1, "startDate": 1, "_id": 1, "eventStatus": 1, "isSuperEvent": 1, "superEventID": 1})
            if not result:
                return []
            return result

        except Exception:
            return []