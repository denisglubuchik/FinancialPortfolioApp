from faststream.rabbit import RabbitBroker
from back.config import RabbitMQSettings

rabbit_broker = RabbitBroker(RabbitMQSettings().RABBITMQ_MQ)
