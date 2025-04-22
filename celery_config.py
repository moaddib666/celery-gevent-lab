from celery import Celery

# Define a variable to switch between Redis and SQS
BROKER_TYPE = "sqs"  # Change to "sqs" for SQS setup

# Redis Configuration
REDIS_BROKER_URL = "redis://localhost:6379/0"
REDIS_BACKEND_URL = "redis://localhost:6379/1"

# SQS Configuration
SQS_BROKER_URL = 'sqs://test:test@localhost:4566'
SQS_TRANSPORT_OPTIONS = {
    'region': 'us-east-1',
    'visibility_timeout': 3600,  # 1 hour timeout for unacknowledged messages
    'polling_interval': 1,  # Polling interval for SQS
    'wait_time_seconds': 20,  # Long polling
    'aws_access_key_id': 'test',
    'aws_secret_access_key': 'test',
    'endpoint_url': 'http://localhost:4566',
    'verify_ssl': False,
    'predefined_queues': {
        'celery-queue.fifo': {
            'url': 'http://localhost:4566/000000000000/celery-queue.fifo',
            'access_key_id': 'test',
            'secret_access_key': 'test',
        },
        'celery-standard': {
            'url': 'http://localhost:4566/000000000000/celery-standard',
            'access_key_id': 'test',
            'secret_access_key': 'test',
        },
    },
}

# Conditional Configuration
if BROKER_TYPE == "redis":
    BROKER_URL = REDIS_BROKER_URL
    BACKEND_URL = REDIS_BACKEND_URL
    TRANSPORT_OPTIONS = {}
else:  # SQS
    BROKER_URL = SQS_BROKER_URL
    BACKEND_URL = None  # You can set a backend if needed
    TRANSPORT_OPTIONS = SQS_TRANSPORT_OPTIONS

app = Celery(
    'tasks',
    broker=BROKER_URL,
    backend=BACKEND_URL,
)

# General Celery Configuration
app.conf.update(
    task_acks_late=True,
    broker_transport_options=TRANSPORT_OPTIONS,
    worker_prefetch_multiplier=1,  # Ensures tasks are consumed one at a time
    task_default_queue='celery-queue.fifo' if BROKER_TYPE == "sqs" else 'default',
    task_default_exchange='celery-queue.fifo' if BROKER_TYPE == "sqs" else 'default',
    task_default_routing_key='celery-queue.fifo' if BROKER_TYPE == "sqs" else 'default',
    task_routes={
        'tasks.long_task': {
            'queue': 'celery-queue.fifo' if BROKER_TYPE == "sqs" else 'default',
        },
        'tasks.simple_task': {
            'queue': 'celery-standard' if BROKER_TYPE == "sqs" else 'default',
        },
    },
    task_serializer='json',
    accept_content=['json'],  # Ignore other content
    result_serializer='json',
    worker_send_task_events=False,
)
