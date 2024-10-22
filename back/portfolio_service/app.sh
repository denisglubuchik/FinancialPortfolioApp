#!/bin/bash

sleep 3

cd /back/portfolio_service
alembic upgrade head
cd ../../

gunicorn back.portfolio_service.portfolio_main:portfolio_app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000