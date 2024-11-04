from back.user_service.message_broker.rabbitmq import rabbit_broker
from faststream.rabbit import RabbitBroker


class Producer:
    def __init__(self, broker):
        self.broker: RabbitBroker = broker

    async def new_user(self, user_id: int, username: str):
        print("trying user created")
        try:
            print("Publishing user_created event")
            await self.broker.publish({"user_id": user_id, "username": username}, "user_created")
        except Exception as e:
            print(e)

    async def update_user(self, user_id: int, username: str):
        await self.broker.publish({"user_id": user_id, "username": username}, "user_updated")

    async def delete_user(self, user_id: int):
        await self.broker.publish({"user_id": user_id}, "user_deleted")


rabbit_producer = Producer(rabbit_broker)
