#!/usr/bin/env bash

source release_base_script.sh

###### EVENTS MANAGER ######
docker build -t ${PROJECT_NAME}/events-manager:${VERSION} .
docker tag ${PROJECT_NAME}/events-manager:${VERSION} 779619664536.dkr.ecr.us-east-2.amazonaws.com/${PROJECT_NAME}/events-manager:${VERSION}
docker push 779619664536.dkr.ecr.us-east-2.amazonaws.com/${PROJECT_NAME}/events-manager:${VERSION}
