# tasks.py
import random
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


@app.task(bind=True, acks_late=True)
def fail_task(self, n: int, *args, **kwargs):
    raise Exception("Task Failed " + str(n))


@app.task(bind=True, acks_late=True)
def success_task(self, n: int, *args, **kwargs):
    return "Task Succeeded " + str(n)


@app.task(bind=True, acks_late=True)
def debug_task(self, *args, **kwargs):
    # print('Request: {0!r}'.format(self.request) + 'Args: {0!r}'.format(args) + 'Kwargs: {0!r}'.format(kwargs))
    print('Args: {0!r}'.format(args) + 'Kwargs: {0!r}'.format(kwargs))
    time.sleep(random.randint(1, 2))