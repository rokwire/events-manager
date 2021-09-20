#!/bin/bash

# how to run it: e.g.,
# ./updategroupids.sh mongodb://localhost:27017/rokwire events-manager

  
MONGO_URI=$1
COLLECTIONNAME=$2


while IFS=$'\t' read -r eventid platformid title createby startdate enddate groupname groupid
do
    echo "$eventid, $platformid, $groupid"
    update=$(mongo $MONGO_URI --quiet --eval "db.$DBNAME.update({_id: ObjectId('"$eventid"')}, {\$set: {createdByGroupId: '"$groupid"', "isGroupPrivate": false}})")
    echo $eventid $update
done < ./prod.tsv

unset IFS
