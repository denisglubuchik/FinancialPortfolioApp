FROM python:3.10

RUN mkdir /back

COPY requirements.txt back

RUN pip install -r back/requirements.txt

COPY back/market_data_service back/market_data_service
COPY back/config.py back/

ENV PYTHONPATH=/back:$PYTHONPATH

# Запуск сервиса
CMD ["python", "/back/market_data_service/main_market_data.py"]