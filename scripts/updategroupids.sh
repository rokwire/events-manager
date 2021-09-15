#!/bin/bash
  
MONGO_URI=$1
DBNAME=$2


while IFS=, read -r eventid platformid title createby startdate enddate groupname groupid
do
    # echo "$eventid, $platformid, $groupid"
    event=$(mongo $MONGO_URI --quiet --eval "db.$DBNAME.find({_id: ObjectId('"$eventid"')})")
    #echo $event
    if [ ! -z "$event" ]; then
        update=$(mongo $MONGO_URI --quiet --eval "db.$DBNAME.update({_id: ObjectId('"$eventid"')}, {\$set: {createdByGroupId: '"$groupid"', "isGroupPrivate": false}})")
        echo $eventid $update
    else
        echo "cannot find $eventid"
    fi

done < ./prod.csv

unset IFS
