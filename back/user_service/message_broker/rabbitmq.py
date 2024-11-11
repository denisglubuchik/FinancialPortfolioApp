from faststream.rabbit import RabbitBroker, RabbitExchange, ExchangeType
from back.config import RabbitMQSettings

rabbit_broker = RabbitBroker(RabbitMQSettings().RABBITMQ_MQ)

user_exchange = RabbitExchange("user_exchange", type=ExchangeType.DIRECT)