import logging
from back.user_service.message_broker.rabbitmq import rabbit_broker, user_exchange
from faststream.rabbit import RabbitBroker

logger = logging.getLogger(__name__)


class Producer:
    def __init__(self, broker, user_exch):
        self.broker: RabbitBroker = broker
        self.user_exch = user_exch

    async def new_user(self, user_id: int, username: str, email: str, telegram_id: int):
        message = {"user_id": user_id, "username": username, "email": email, "telegram_id": telegram_id}
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

    async def email_verification(self, user_id, code):
        message = {
            "user_id": user_id, 
            "subject": "Код верификации FinancialPortfolio Bot",
            "message": f"""Здравствуйте!

Вы запросили подтверждение email адреса в FinancialPortfolio Bot.

Ваш код верификации: {code}

Код действителен в течение 10 минут.

Если вы не запрашивали подтверждение email, просто проигнорируйте это письмо.

С уважением,
Команда FinancialPortfolio Bot"""
        }
        try:
            await self.broker.publish(message, "email")
            logger.info(f"Email verification message sent to queue for user_id: {user_id}")
        except Exception as e:
            logger.error(f"Failed to send email verification message for user_id {user_id}: {e}")

    async def password_changed(self, user_id):
        await self.broker.publish({"user_id": user_id, "subject": "Password changed",
                                   "message": "Your password has been changed"}, "email")


rabbit_producer = Producer(rabbit_broker, user_exchange)
