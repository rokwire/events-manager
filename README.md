# events-manager
The goal of the events manager is to provide a web interface to manage events in the Rokwire platform. This includes the crawling events from event sources, the approval of the events ingestion to Rokwire events building block and the visualization of the events, etc. 

## Setup Environment

```
virtualenv -p python3 venv
source venv/bin/activate
pip install -r requirements.txt
```

## Run in Development Mode
This repository should be put inside a folder `/flaskr`. Run these commands outside the folder.

For Linux and Mac:
```
export FLASK_APP=flaskr
export FLASK_ENV=develop
flask run
```
For Windows:
```
set FLASK_APP=flaskr
set FLASK_ENV=develop
flask run
```
