from faststream.rabbit import RabbitRouter, RabbitExchange, ExchangeType

from back.notification_service.db.dao import UsersDAO, NotificationsDAO
from back.notification_service.utils import send_email

rabbit_router = RabbitRouter()

user_exchange = RabbitExchange("user_exchange", type=ExchangeType.DIRECT)


@rabbit_router.subscriber("notification_user_created", user_exchange)
async def handle_new_user(message):
    user_id = message["user_id"]
    email = message["email"]
    await UsersDAO.insert(id=user_id, email=email)


@rabbit_router.subscriber("notification_user_updated", user_exchange)
async def handle_update_user(message):
    user_id = message["user_id"]
    email = message["email"]
    await UsersDAO.update(user_id, email=email)


@rabbit_router.subscriber("notification_user_deleted", user_exchange)
async def handle_delete_user(message):
    user_id = message["user_id"]
    await UsersDAO.delete(user_id)


@rabbit_router.subscriber("email_verification")
async def handle_email_verification(message):
    user_id = message["user_id"]
    email = message["email"]
    subject = message["subject"]
    body = message["message"]
    notification_type = "email"
    await send_email(email, subject, body)
    await NotificationsDAO.insert(
        user_id=user_id,
        title=subject,
        message=body,
        notification_type=notification_type
    )
