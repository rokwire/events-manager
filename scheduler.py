#  Copyright 2020 Board of Trustees of the University of Illinois.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.events import *
from .utilities.sourceEvents import start
import logging
from time import gmtime
logging.Formatter.converter = gmtime
logging.basicConfig(level=logging.INFO, datefmt='%Y-%m-%dT%H:%M:%S',
                    format='%(asctime)-15s.%(msecs)03dZ %(levelname)-7s [%(threadName)-10s] : %(name)s - %(message)s')
__logger = logging.getLogger("scheduler.py")


def event_exception_listener(event):
    if event.exception:
        __logger.error("Event Scheduler found an issue with job {} and code {} at {}".format(
            event.job_id, event.code, event.scheduled_run_time
        ))
        __logger.error("Event error traceback are: ")
        __logger.error(event.traceback)

def event_start_listener(event):
    __logger.info("Scheduler starts.")

def event_shutdown_listener(event):
    __logger.info("Scheduler shuts down.")

def event_completed_listener(event):
    __logger.info("Job {} has been completed".format(event.job_id))

def scheduler_add_job(current_app, scheduler, func, start_date, *args, **kwargs):
    
    if not scheduler or not func:
        __logger.error("Error not found scheduler instance or function")

    elif not current_app:
        __logger.error("Job here should run under app context")

    else:
        def func_wrapper(func, *args, **kwargs):
            with current_app.app_context():
                func(*args, **kwargs)

        try:
            scheduler.add_job(func_wrapper, 'date', run_date=start_date, args=(func, *args), kwargs=kwargs)
        except Exception as ex:
            __logger.exception(ex)
            __logger.error("Error adding job")



def create_scheduler(app):
    today = datetime.today()
    startDate = datetime(today.year, today.month, today.day, int(app.config['SCHEDULER_HOUR']), int(app.config['SCHEDULER_MINS']), 00, 00)
    scheduler = BackgroundScheduler({'apscheduler.timezone': 'US/Central'})
    scheduler.add_listener(event_exception_listener, EVENT_JOB_ERROR)
    scheduler.add_listener(event_start_listener, EVENT_SCHEDULER_STARTED)
    scheduler.add_listener(event_shutdown_listener, EVENT_SCHEDULER_SHUTDOWN)
    scheduler.add_listener(event_completed_listener, EVENT_JOB_EXECUTED)
    def create_start(app):
        with app.app_context():
            start()
    
    scheduler.add_job(create_start, trigger='interval', args=[app], days=1, start_date=startDate)
    __logger.info("Schedule at {}:{}".format(app.config['SCHEDULER_HOUR'], app.config['SCHEDULER_MINS']))
    return scheduler

def drop_scheduler(scheduler):
    scheduler.remove_all_jobs()
    scheduler.shutdown(wait=False)
