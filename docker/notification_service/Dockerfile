FROM python:3.10

RUN mkdir /back

COPY requirements.txt back

RUN pip install -r back/requirements.txt

COPY back/notification_service back/notification_service
COPY back/config.py back/

RUN chmod a+x /back/notification_service/app.sh

#CMD ["faststream", "run", "back.notification_service.notification_main:notification_app", "--workers", "4"]
