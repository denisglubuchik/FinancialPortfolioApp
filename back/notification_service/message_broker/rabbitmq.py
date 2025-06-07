from faststream.rabbit import RabbitBroker

from back.config import RabbitMQSettings
from back.notification_service.message_broker.consumer import rabbit_router

rabbit_broker = RabbitBroker(RabbitMQSettings().RABBITMQ_MQ)
rabbit_broker.include_router(rabbit_router) 