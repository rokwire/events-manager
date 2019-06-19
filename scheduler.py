from datetime import datetime
from flask import current_app
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.events import *

from .utilities.sourceEvents import start

def taskWrapper(func, app, *args, **kwargs):
    with app.app_context():
        return func(*args, **kwargs)

def event_exception_listener(event):
    if event.exception:
        print("Event Scheduler found an issue with job {} and code {} at {}".format(
            event.job_id, event.code, event.scheduled_run_time
        ))

def event_start_listener(event):
    print("Scheduler starts.")

def event_shutdown_listener(event):
    print("Scheduler shuts down.")

def create_scheduler():
    scheduler=BackgroundScheduler(timezone="America/Chicago")
    today = datetime.today()
    startDate = datetime(today.year, today.month, today.day, 23, 59, 59, 59)
    scheduler.add_listener(event_exception_listener, mask=EVENT_JOB_ERROR)
    scheduler.add_listener(event_start_listener, mask=EVENT_SCHEDULER_STARTED)
    scheduler.add_listener(event_shutdown_listener, mask=EVENT_SCHEDULER_SHUTDOWN)
    scheduler.add_job(func=taskWrapper, kwargs={"func": start, "app": current_app._get_current_object()}, trigger='interval', days=1, start_date=startDate, timezone="America/Chicago")
    scheduler.start()
    return scheduler

def drop_scheduler(scheduler):
    scheduler.remove_all_jobs()
    scheduler.shutdown(wait=False)
    
def schedule_downloading(time, urls):
    current_app.scheduler.add_job(func=taskWrapper, kwargs={"func": start, "app": current_app._get_current_object(), "targets": urls}, next_run_time=time)
    