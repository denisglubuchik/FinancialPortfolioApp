FROM python:3.10

RUN mkdir /back

COPY requirements.txt back

RUN pip install -r back/requirements.txt

COPY back/user_service back/user_service
COPY back/config.py back/

RUN chmod a+x /back/user_service/app.sh

#CMD ["gunicorn", "back.user_service.user_main:user_app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind=0.0.0.0:8001"]
