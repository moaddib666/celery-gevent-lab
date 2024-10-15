from celery import Celery

# Create Celery app instance
app = Celery(
    'tasks',
    # sqs://aws_access_key_id:aws_secret_access_key@
    broker='sqs://test:test@localhost:4566',
    backend='rpc://',
)

# AWS Credentials and LocalStack configuration
app.conf.update(
    task_acks_late=True,  # Enable late acknowledgment for tasks
    broker_transport_options={
        'region': 'us-east-1',  # Ensure it matches LocalStack's region
        'visibility_timeout': 3600,  # 1 hour timeout for unacknowledged messages
        'polling_interval': 1,  # Polling interval for checking the SQS queue
        'wait_time_seconds': 20,  # Long polling for SQS
        'queue_name_prefix': 'celery-',  # Optional queue name prefix for Celery queues
        'aws_access_key_id': 'test',  # Dummy credentials for LocalStack
        'aws_secret_access_key': 'test',  # Dummy credentials for LocalStack
        'endpoint_url': 'http://localhost:4566/000000000/',  # LocalStack URL
        'verify_ssl': False,  # LocalStack does not use SSL verification
    },
    worker_prefetch_multiplier=1,  # Ensures tasks are consumed one at a time
)
