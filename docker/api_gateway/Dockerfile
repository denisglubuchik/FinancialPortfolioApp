FROM python:3.10

RUN mkdir /back

COPY requirements.txt back

RUN pip install -r back/requirements.txt

COPY back/gateway back/gateway
COPY back/config.py back/
COPY back/logging.py back/

CMD ["gunicorn", "back.gateway.gateway_main:api_gateway", "--workers", "3", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind=0.0.0.0:7777"]
