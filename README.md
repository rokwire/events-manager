# Events Manager
The goal of the Events Manager is to provide a web interface to manage events in the Rokwire platform. This includes the crawling events from event sources, the approval of the events ingestion to Rokwire events building block and the visualization of the events, etc.

## Run in Development Mode
MongoDB's service needs to be started and a Mongo Shell needs to be connected in a separate terminal instance

- For MacOS
```
brew services start mongodb-community@4.2
mongo
```

- Ubuntu (The daemon-reload command isn't required)
```
sudo systemctl daemon-reload
sudo systemctl start mongod
mongo
```

This repository should be put inside `/events-manager` and run outside the folder. There are two ways to do so:

The first one:

- (Linux or MAC):
```
export FLASK_APP=events-manager
export FLASK_ENV=development
flask run
```

- (Windows):
```
set FLASK_APP=eventsmanager
set FLASK_ENV=development
flask run
```

The second one:

- create a file called .flaskenv
- fill in file with:
    - FLASK_APP=\_\_init\_\_.py
    - FLASK_ENV=development
    - FLASK_DEBUG=1

## Setup Environment

```
virtualenv -p python3 venv
source venv/bin/activate
pip install -r requirements.txt
```

## Install pre-commit hooks
```bash
pip install -r requirements-dev.txt
pre-commit install
```

The following environment variables need to be set when running on development machine. This is not required when running within AWS.
```
AWS_ACCESS_KEY_ID=<AWS Access Key ID>
AWS_SECRET_ACCESS_KEY=<AWS Secret Access Key>
```


## Run as Docker Container in Local
```
cd events-manager
./docker.sh
docker run --rm --name events -v $PWD/config.py:/app/events-manager/config.py -p 5000:5000 rokwire/events-manager
```

## MongoDB Setup

MongoDB needs to be installed for the flask app to run and interface with a database

- For MacOS, prerequisites are having XCode and Homebrew
```
brew tap mongodb/brew
brew install mongodb-community@4.2
```
- For Ubuntu LTS releases
```
wget -qO - https://www.mongodb.org/static/pgp/server-4.2.asc | sudo apt-key add -
```
The above should work, but in case a gnupg error is encountered
```
sudo apt-get install gnupg
wget -qO - https://www.mongodb.org/static/pgp/server-4.2.asc | sudo apt-key add -
```
Create a list file for MongoDB
```
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu bionic/mongodb-org/4.2 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-4.2.list
```
Reload and Install
```
sudo apt-get update
sudo apt-get install -y mongodb-org
```

The template setup configuration exists in config.py.template, to run locally a new file config.py needs to be created accounting for changes based on your local environment setup.  
