from faststream import FastStream
from faststream.rabbit import RabbitBroker

from back.config import RabbitMQSettings

rabbit_broker = RabbitBroker(RabbitMQSettings().RABBITMQ_MQ)

notification_app = FastStream(rabbit_broker)


@notification_app.after_startup
async def start_rabbit():
    await rabbit_broker.start()


@notification_app.after_shutdown
async def stop_rabbit():
    await rabbit_broker.close()
