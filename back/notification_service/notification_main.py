from faststream import FastStream
from faststream.rabbit import RabbitBroker

from back.config import RabbitMQSettings
from back.notification_service.message_broker.consumer import rabbit_router

rabbit_broker = RabbitBroker(RabbitMQSettings().RABBITMQ_MQ)
rabbit_broker.include_router(rabbit_router)

notification_app = FastStream(rabbit_broker)


@notification_app.after_startup
async def start_rabbit():
    await rabbit_broker.start()


@notification_app.after_shutdown
async def stop_rabbit():
    await rabbit_broker.close()
