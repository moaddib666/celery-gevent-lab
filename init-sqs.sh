#!/bin/bash

echo "Creating SQS queues..."

awslocal sqs create-queue \
    --queue-name celery-queue.fifo \
    --attributes FifoQueue=true,ContentBasedDeduplication=false

awslocal sqs create-queue \
    --queue-name celery-standard

echo "Queues created!"
