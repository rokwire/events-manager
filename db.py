import pymongo

from flask import current_app



# Currently, assume there are only one database
# Also, in query, there are no range filter like x>1 for mysql

# TODO: insert try and catch function
# TODO: complete mysql function if needed

def find_one(co_or_ta, filter=None):
    
    dbType = current_app.config['DBTYPE']
    dbClient = current_app.config['DBCLIENT']
    if co_or_ta is None or filter is None:
        return 
    
    if dbType == "mongoDB":
        collection = dbClient.db.get_collection(co_or_ta)
        return collection.find_one(filter)
    
    elif dbType == "mysql":
        cursor = dbClient.get_db().cursor()
        queryAction = "SELECT * FROM {} WHERE {}".format(co_or_ta)
        queryCondition = '1=1'
        for (key, value) in filter:
            queryCondition = "{} AND {}={}".format(queryCondition, key, value)
        query = "{} {}".format(queryAction, queryCondition)
        try:
            cursor.execute(query)
            result = cursor.fetchone()
            return result
        except:
            print("Error: unable to fetch data")

def insert_one(co_or_ta, entry=None):
    dbType = current_app.config['DBTYPE']
    dbClient = current_app.config['DBCLIENT']
    if entry is None or co_or_ta is None:
        return
    
    if dbType == "mongoDB":
        collection = dbClient.db.get_collection(co_or_ta)
        collection.insert_one(entry)
    elif dbType == "mysql":
        pass

def find_one_and_update(co_or_ta, filter=None, update=None):
    dbClient = current_app.config['DBCLIENT']
    dbType = current_app.config['DBTYPE']
    if co_or_ta is None or filter is None or update is None:
        return
    
    if dbType == "mongoDB":
        collection = dbClient.db.get_collection(co_or_ta)
        collection = dbClient.find_one_and_update(filter, update)
    elif dbType == "mysql":
        pass