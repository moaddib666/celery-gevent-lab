# CELERY GEVENT/EVENTLET LAB:

Problem: Celery configured with late acks and gevent/eventlet workers is not working as expected.
Reason: Celery _pending_tasks is not being executed after shutdown signal is received.
Solution: Fix the synloop and Consumer.shutdown() method to execute _pending_tasks before pasisng the shutdown to
blueprints.

## Steps to reproduce:
0. Install the requirements for 
`pip install celery[sqs]`

```bash
1. Start the localstack with the following command:

```bash
docker compose up -d
```

2. Start the celery worker with the following command:

```bash
celery -A tasks worker --loglevel=info -P gevent --concurrency=1
```

3. Run the script that sends a task to the worker:

```bash
python3 trigger_tasks.py
```

4. Stop the worker with SIGINT (Ctrl+C) or SIGTERM (kill -15 <pid>).
5. Check the logs of the worker and the scrip
6. Chek that SQS does not have any messages related to the last task executed by worker.
7. Start the worker again and check the logs new task messages are being processed.

### Expected behavior:

```bash
/Users/moaddib/PycharmProjects/celeryLab/pythonProject/.venv/bin/python -m celery -A tasks worker --loglevel=info --pool=gevent --concurrency=1 

 -------------- celery@asmadeus.local v5.5.0rc1 (immunity)
--- ***** ----- 
-- ******* ---- macOS-14.6.1-x86_64-i386-64bit 2024-10-15 14:27:22
- *** --- * --- 
- ** ---------- [config]
- ** ---------- .> app:         tasks:0x10da7ae90
- ** ---------- .> transport:   sqs://test:**@localhost:4566//
- ** ---------- .> results:     rpc://
- *** --- * --- .> concurrency: 1 (gevent)
-- ******* ---- .> task events: OFF (enable -E to monitor tasks in this worker)
--- ***** ----- 
 -------------- [queues]
                .> celery           exchange=celery(direct) key=celery


[tasks]
  . tasks.long_task
  . tasks.simple_task

[2024-10-15 14:27:23,145: INFO/MainProcess] Connected to sqs://test:**@localhost:4566//
[2024-10-15 14:27:23,253: INFO/MainProcess] Global QoS is disabled. Prefetch count in now static.
[2024-10-15 14:27:23,278: INFO/MainProcess] celery@asmadeus.local ready.
[2024-10-15 14:27:23,303: INFO/MainProcess] Task tasks.simple_task[9d33fbac-6d44-472e-905b-dd74cc728abb] received
[2024-10-15 14:27:23,304: WARNING/MainProcess] 9d33fbac-6d44-472e-905b-dd74cc728abb: Sleeping 9 seconds

worker: Hitting Ctrl+C again will initiate cold shutdown, terminating all running tasks!

worker: Warm shutdown (MainProcess)
[2024-10-15 14:27:32,307: WARNING/MainProcess] 9d33fbac-6d44-472e-905b-dd74cc728abb: Slept 9 seconds
[2024-10-15 14:27:32,522: INFO/MainProcess] Task tasks.simple_task[9d33fbac-6d44-472e-905b-dd74cc728abb] succeeded in 9.217870448992471s: None
```





<kombu.transport.SQS.Channel object at 0x10fe3cc90>
self.Message
<class 'kombu.transport.virtual.base.Message'>


# TEST HOW CHAIN WORKS

## Patch for kombu package
Before running this lab, you need to apply the following patch to the kombu package:
```
feat(qos)__extend_QoS_class_to_support_FIFO_message_processing_with_GroupedQueue.patch
```

This patch extends the QoS class in kombu to support FIFO message processing with GroupedQueue. It adds several methods to handle FIFO queues and modifies the behavior of basic_consume and basic_ack.

To apply the patch:
1. Locate your kombu installation directory (typically in your virtual environment's site-packages)
2. Apply the patch using the following command:
   ```bash
   patch -p1 < feat\(qos\)__extend_QoS_class_to_support_FIFO_message_processing_with_GroupedQueue.patch
   ```
3. Ensure that the qos module from this project is available in your Python path
