# tasks.py

import time

from celery_config import app


@app.task(bind=True, acks_late=True)
def long_task(self):
    print(f"Task {self.request.id} started")
    time.sleep(2)
    print(f"Task {self.request.id} finished")
    return 'Task Completed'


@app.task(bind=True, acks_late=True)
def simple_task(task, sleep_seconds=1):
    _id = task.request.id
    print("{}: Sleeping {} seconds".format(_id, sleep_seconds))
    time.sleep(sleep_seconds)

    print("{}: Slept {} seconds".format(_id, sleep_seconds))
