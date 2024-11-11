from back.user_service.message_broker.rabbitmq import rabbit_broker, user_exchange
from faststream.rabbit import RabbitBroker


class Producer:
    def __init__(self, broker, user_exch):
        self.broker: RabbitBroker = broker
        self.user_exch = user_exch

    async def new_user(self, user_id: int, username: str, email: str):
        message = {"user_id": user_id, "username": username, "email": email}
        try:
            await self.broker.publish(message, routing_key="portfolio_user_created", exchange=self.user_exch)
            await self.broker.publish(message, routing_key="notification_user_created", exchange=self.user_exch)
        except Exception as e:
            print(e)

    async def update_user(self, user_id: int, username: str = None, email: str = None):
        message = {"user_id": user_id, "username": username, "email": email}
        await self.broker.publish(message, routing_key="portfolio_user_updated", exchange=self.user_exch)
        await self.broker.publish(message, routing_key="notification_user_updated", exchange=self.user_exch)

    async def delete_user(self, user_id: int):
        message = {"user_id": user_id}
        await self.broker.publish(message, routing_key="portfolio_user_deleted", exchange=self.user_exch)
        await self.broker.publish(message, routing_key="notification_user_deleted", exchange=self.user_exch)

    async def email_verification(self, user_id, email, code):
        await self.broker.publish({"user_id": user_id, "email": email, "subject": "Email verification",
                                   "message": code}, "email_verification")


rabbit_producer = Producer(rabbit_broker, user_exchange)
