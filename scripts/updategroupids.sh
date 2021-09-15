#!/bin/bash

# how to run it: e.g.,
# ./updategroupids.sh mongodb://localhost:27017/rokwire events-manager

  
MONGO_URI=$1
COLLECTIONNAME=$2


while IFS=, read -r eventid platformid title createby startdate enddate groupname groupid
do
    # echo "$eventid, $platformid, $groupid"
    event=$(mongo $MONGO_URI --quiet --eval "db.$COLLECTIONNAME.find({_id: ObjectId('"$eventid"')})")
    #echo $event
    if [ ! -z "$event" ]; then
        update=$(mongo $MONGO_URI --quiet --eval "db.$COLLECTIONNAME.update({_id: ObjectId('"$eventid"')}, {\$set: {createdByGroupId: '"$groupid"', "isGroupPrivate": false}})")
        echo $eventid $update
    else
        echo "cannot find $eventid"
    fi

done < ./prod.csv

unset IFS
