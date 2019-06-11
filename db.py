import pymongo
from pymongo.errors import ConnectionFailure
from pymongo.results import InsertOneResult, UpdateResult
from flask import current_app,g

######################################################################
### Basic DB creation and access functions
######################################################################
def get_db():
    if 'dbclient' not in g:
        if current_app.config['DBTYPE'] == 'mongoDB':
            try:
                g.dbclient = pymongo.MongoClient(
                    host=current_app.config['MONGO_HOST'],
                    port=current_app.config['MONGO_PORT'],
                )
            except ConnectionFailure:
                print("MongoDB connection failed.")
                if 'dbclient' in g:
                    g.pop('dbclient', None)
                return None
            g.db = g.dbclient.get_database(name=current_app.config['MONGO_DATABASE'])
    return g.db


def close_db(e=None):
    if current_app.config['DBTYPE'] == 'mongoDB':
        g.pop('db', None)
        dbclient = g.pop('dbclient', None)
        if dbclient is not None:
            dbclient.close()


def init_db(app):
    app.teardown_appcontext(close_db)


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
            return collection.find_one(filter=condition, *args, **kwargs)
        except TypeError:
            print("Invalid arguments inserted")
            return {}
        except Exception:
            print("Unknown error using find_one")
            return {}


def find_one_and_update(co_or_ta, condition=None, update=None, **kwargs):
    db = get_db()
    dbType = current_app.config['DBTYPE']

    if co_or_ta is None or condition is None or update is None or db is None:
        return {}
    
    if dbType == "mongoDB":
        try:
            collection = db.get_collection(co_or_ta)
            return collection.find_one_and_update(condition, update, **kwargs)
        except TypeError:
            print("Invalid arguments inserted")
            return {}
        except Exception:
            print("Unknown error using find_one_and_update")
            return {}


def find_all(co_or_ta, **kwarg):
    db = get_db()
    dbType = current_app.config['DBTYPE']

    if co_or_ta is None or db is None:
        return []
    
    if dbType == "mongoDB":
        try:
            collection = db.get_collection(co_or_ta)
            return collection.find(**kwarg)
        except TypeError:
            print("Invalid arguments inserted")
            return []
        except Exception:
            print("Unknown error using find_all")
            return []


def insert_one(co_or_ta, document=None, **kwargs):
    db = get_db()
    dbType = current_app.config['DBTYPE']

    if document is None or co_or_ta is None or db is None:
        return InsertOneResult()

    if dbType == "mongoDB":
        try:
            collection = db.get_collection(co_or_ta)
            return collection.insert_one(document=document, **kwargs)
        except:
            return UpdateResult()


def update_one(co_or_ta, condition=None, update=None, **kwargs):
    db = get_db()
    dbType = current_app.config['DBTYPE']

    if update is None or co_or_ta is None or condition is None or db is None:
        return UpdateResult()

    if dbType == "mongoDB":
        try:
            collection = db.get_collection(co_or_ta)
            return collection.update_one(condition, update, **kwargs)
        except Exception:
            return UpdateResult()


