from faststream.rabbit import RabbitBroker
from back.config import RabbitMQSettings

rabbit_broker = RabbitBroker(RabbitMQSettings().RABBITMQ_MQ)


async def new_user(user_id: int, username: str):
    await rabbit_broker.publish({"user_id": user_id, "username": username},
                                queue="user_created")


async def update_user(user_id: int, username: str):
    await rabbit_broker.publish({"user_id": user_id, "username": username},
                                queue="user_updated")


async def delete_user(user_id: int):
    await rabbit_broker.publish({"user_id": user_id}, queue="user_deleted")

