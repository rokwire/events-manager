import pymongo
from flask import current_app,g

# Currently, assume there are only one database
# Also, in query, there are no range filter like x>1 for mysql

# TODO: insert try and catch function
# TODO: complete mysql function if needed

def get_db():
    if 'dbclient' not in g:
        if current_app.config['DBTYPE'] == 'mongoDB':
            g.dbclient = pymongo.MongoClient(
                host=current_app.config['MONGO_HOST'],
                port=current_app.config['MONGO_PORT'],
            )
            g.db = g.dbclient.get_database(name=current_app.config['MONGO_DATABASE'])
    
    return g.db

def close_db(e=None):
    if current_app.config['DBTYPE'] == 'mongoDB':
        db = g.pop('db', None)
        dbclient = g.pop('dbclient', None)
        if dbclient is not None:
            dbclient.close()

def init_db(app):
    app.teardown_appcontext(close_db)

def find_one(co_or_ta, filter=None, *args, **kwargs):
    
    db = get_db()
    dbType = current_app.config['DBTYPE']
    
    if co_or_ta is None:
        return 
    
    if dbType == "mongoDB":
        collection = db.get_collection(co_or_ta)
        return collection.find_one(filter, *args, **kwargs)
    

def insert_one(co_or_ta, document=None, **kwargs):

    db = get_db()
    dbType = current_app.config['DBTYPE']

    if document is None or co_or_ta is None:
        return
    
    if dbType == "mongoDB":
        collection = db.get_collection(co_or_ta)
        collection.insert_one(document=document, **kwargs)

def find_one_and_update(co_or_ta, filter=None, update=None, **kwargs):
    db = get_db()
    dbType = current_app.config['DBTYPE']

    if co_or_ta is None or filter is None or update is None:
        return
    
    if dbType == "mongoDB":
        collection = db.get_collection(co_or_ta)
        db.find_one_and_update(filter, update, **kwargs)

def find_all(co_or_ta, **kwarg):

    db = get_db()
    dbType = current_app.config['DBTYPE']

    if co_or_ta is None:
        return
    
    if dbType == "mongoDB":
        collection = db.get_collection(co_or_ta)
        return collection.find(**kwarg)



