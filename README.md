# events-manager
The goal of the events manager is to provide a web interface to manage events in the Rokwire platform. This includes the crawling events from event sources, the approval of the events ingestion to Rokwire events building block and the visualization of the events, etc. 

## Setup Environment

```
virtualenv -p python3 venv
source venv/bin/activate
pip install -r requirements.txt
```

## Run in Development Mode
There are two ways to do so:

The first one (Linux or MAC):
- export FLASK_APP=eventsmanager
- export FLASK_ENV=development
- flask run

(Windows):
- set FLASK_APP=eventsmanager
- set FLASK_ENV=development
- flask run

The second one:
- create a file called .flaskenv
- fill in file with: 
    - FLASK_APP=\_\_init\_\_.py
    - FLASK_ENV=development
    - FLASK_DEBUG=1

