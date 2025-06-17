FROM python:3.10

RUN mkdir /back

COPY requirements.txt back

RUN pip install -r back/requirements.txt

COPY back/market_data_service back/market_data_service
COPY back/config.py back/
COPY back/logging.py back/

RUN chmod a+x /back/market_data_service/app.sh

ENV PYTHONPATH=/:$PYTHONPATH

CMD ["back/market_data_service/app.sh"]