#!/bin/bash

sleep 3

cd /back/notification_service
alembic upgrade head
cd ../../

gunicorn back.notification_service.notification_main:notification_app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8002
#faststream run back.notification_service.notification_main:notification_app --workers 4