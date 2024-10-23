#!/bin/bash

sleep 3

cd /back/user_service
alembic upgrade head
cd ../../

gunicorn back.user_service.user_main:user_app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8001