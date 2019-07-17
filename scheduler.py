from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.events import *
from .utilities.sourceEvents import start


def event_exception_listener(event):
    if event.exception:
        print("Event Scheduler found an issue with job {} and code {} at {}".format(
            event.job_id, event.code, event.scheduled_run_time
        ))
        print("Event error traceback are: ")
        print(event.traceback)

def event_start_listener(event):
    print("Scheduler starts.")

def event_shutdown_listener(event):
    print("Scheduler shuts down.")

def event_completed_listener(event):
    print("Job {} has been completed".format(event.job_id))

def scheduler_add_job(current_app, scheduler, func, start_date, *args, **kwargs):
    
    if not scheduler or not func:
        print("Error not found scheduler instance or function") 

    elif not current_app:
        print("Job here should run under app context")

    else:
        def func_wrapper(func, *args, **kwargs):
            with current_app.app_context():
                func(*args, **kwargs)

        try:
            scheduler.add_job(func_wrapper, 'date', run_date=start_date, args=(func, *args), kwargs=kwargs)
        except Exception:
            print("Error adding job")



def create_scheduler(app):
    today = datetime.today()
    startDate = datetime(today.year, today.month, today.day, 23, 59, 59, 59)
    scheduler = BackgroundScheduler(timezone="America/Chicago")
    scheduler.add_listener(event_exception_listener, EVENT_JOB_ERROR)
    scheduler.add_listener(event_start_listener, EVENT_SCHEDULER_STARTED)
    scheduler.add_listener(event_shutdown_listener, EVENT_SCHEDULER_SHUTDOWN)
    scheduler.add_listener(event_completed_listener, EVENT_JOB_EXECUTED)
    def create_start(app):
        with app.app_context():
            start()

    scheduler.add_job(create_start, trigger='interval', args=[app], days=1, start_date=startDate, timezone="America/Chicago")
    return scheduler

def drop_scheduler(scheduler):
    scheduler.remove_all_jobs()
    scheduler.shutdown(wait=False)
