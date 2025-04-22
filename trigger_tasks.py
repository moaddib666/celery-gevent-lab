import uuid
from celery import xmap, xstarmap
from celery_config import app
from tasks import long_task, simple_task, fail_task, success_task, debug_task


def main_1():
    num_tasks = 1_000  # Dispatch 10 tasks
    for _ in range(num_tasks):
        result = long_task.apply_async()
        print(f"Dispatched Task ID: {result.id}")


def main_2():
    for i in range(10):
        result = simple_task.delay(i)
        print(f"Dispatched Task {result.id}")


def main_3():
    message_group_ids = ["group1", "group2", "group3"]
    for i in range(5):
        for message_group_id in message_group_ids:
            deduplication_id = uuid.uuid4()
            message_properties = {
                "MessageGroupId": str(message_group_id),
                "MessageDeduplicationId": str(deduplication_id),
            }
            queue = "celery-queue.fifo"
            print(f"Dispatching Task to Queue: {queue} - Message Properties: {message_properties}")
            # long_task.apply_async(
            #     (), {}, queue=queue
            # )
            result = app.send_task("tasks.debug_task", (str(message_group_id) + f"- {i}", ), queue=queue, **message_properties)

            print(f"Dispatched Task ID: {result.id}")

def _schedule_task(task,  group_id, i, args=None):
    if not args:
        args = (str(group_id) + f"- {i}", )
    deduplication_id = uuid.uuid4()
    message_properties = {
        "MessageGroupId": str(group_id),
        "MessageDeduplicationId": str(deduplication_id),
    }
    queue = "celery-queue.fifo"
    print(f"Dispatching Task to Queue: {queue} - Message Properties: {message_properties}")
    result = app.send_task(
        task, args, {}, queue=queue, **message_properties
    )
    print(f"Dispatched Task ID: {result.id}")

def main_4():
    chain = success_task.s(1) | fail_task.s(1) | success_task.s(2) | success_task.s(3)
    result = chain.apply_async()
    mapping = xmap(success_task.s, [1, 2, 3])
    print(f"Dispatched Task ID: {result.id}")


if __name__ == "__main__":

    # _schedule_task("tasks.debug_task", "group1", 1)
    # _schedule_task("tasks.debug_task", "group1", 2)
    # _schedule_task("tasks.debug_task", "group2", 1)
    #
    # _schedule_task("tasks.debug_task", "group1", 3)
    # _schedule_task("tasks.debug_task", "group2", 2)
    # _schedule_task("tasks.debug_task", "group2", 3)
    #
    # _schedule_task("tasks.debug_task", "group1", 4)
    # _schedule_task("tasks.debug_task", "group2", 4)
    _schedule_task("tasks.debug_task", "group3", 1)


    _schedule_task("tasks.debug_task", "group4", 1)
    _schedule_task("tasks.debug_task", "group4", 2)
    _schedule_task("tasks.debug_task", "group5", 1)
    _schedule_task("tasks.debug_task", "group5", 2)
    _schedule_task("tasks.debug_task", "group6", 1)
    _schedule_task("tasks.debug_task", "group6", 2)
    _schedule_task("tasks.debug_task", "group7", 1)
    _schedule_task("tasks.debug_task", "group7", 2)
    _schedule_task("tasks.debug_task", "group8", 1)
    _schedule_task("tasks.debug_task", "group8", 2)
    _schedule_task("tasks.debug_task", "group9", 1)


