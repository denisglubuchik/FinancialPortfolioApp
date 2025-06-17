FROM python:3.10

RUN mkdir /back

COPY requirements.txt back

RUN pip install -r back/requirements.txt

COPY back/portfolio_service back/portfolio_service
COPY back/config.py back/
COPY back/logging.py back/

RUN chmod a+x /back/portfolio_service/app.sh

#CMD ["gunicorn", "back.portfolio_service.portfolio_main:portfolio_app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind=0.0.0.0:8000"]
