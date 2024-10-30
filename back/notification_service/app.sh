#!/bin/bash

sleep 3

cd /back/notification_service
alembic upgrade head
cd ../../

faststream run back.notification_service.notification_main:notification_app --workers 4