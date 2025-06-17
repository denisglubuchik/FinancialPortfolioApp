import logging
from faststream.rabbit import RabbitExchange, ExchangeType, RabbitRouter

from back.config import RabbitMQSettings
from back.notification_service.db.dao import UsersDAO, NotificationsDAO
from back.notification_service.utils import send_email

logger = logging.getLogger(__name__)

rabbit_router = RabbitRouter()

user_exchange = RabbitExchange("user_exchange", type=ExchangeType.DIRECT)



@rabbit_router.subscriber("notification_user_created", user_exchange)
async def handle_new_user(message):
    user_id = message["user_id"]
    email = message["email"]
    telegram_id = message["telegram_id"]
    logger.info(f"Creating new user in notification service: user_id={user_id}, email={email}, telegram_id={telegram_id}")
    await UsersDAO.insert(id=user_id, email=email, telegram_id=telegram_id)


@rabbit_router.subscriber("notification_user_updated", user_exchange)
async def handle_update_user(message):
    user_id = message["user_id"]
    email = message["email"]
    logger.info(f"Updating user in notification service: user_id={user_id}, email={email}")
    await UsersDAO.update(user_id, email=email)


@rabbit_router.subscriber("notification_user_deleted", user_exchange)
async def handle_delete_user(message):
    user_id = message["user_id"]
    logger.info(f"Deleting user in notification service: user_id={user_id}")
    await UsersDAO.delete(user_id)


@rabbit_router.subscriber("email")
async def handle_email_verification(message):
    logger.info(f"Received email message: {message} in RabbitMQ")
    
    try:
        user_id = message["user_id"]
        subject = message["subject"]
        body = message["message"]
        notification_type = "email"

        logger.info(f"Processing email for user_id: {user_id}")

        user = await UsersDAO.find_one_or_none(id=user_id)
        if not user:
            logger.error(f"User {user_id} not found in notification service")
            return
            
        email = user.email
        if not email:
            logger.error(f"No email found for user {user_id}")
            return
            
        logger.info(f"Sending email to: {email}")
        logger.info(f"Subject: {subject}")

        await send_email(email, subject, body)
        logger.info(f"Email sent successfully to {email}")
        
        await NotificationsDAO.insert(
            user_id=user_id,
            title=subject,
            message=body,
            notification_type=notification_type
        )
        logger.info(f"Notification record created for user {user_id}")
        
    except Exception as e:
        logger.error(f"Error in handle_email_verification: {e}", exc_info=True)


@rabbit_router.subscriber("price_change_alert")
async def handle_price_change_alert(message):
    """Обработка уведомлений об изменении цен"""
    try:
        user_id = message["user_id"]
        asset_name = message["asset_name"]
        asset_symbol = message["asset_symbol"] 
        change_percent = message["change_percent"]
        current_price = message["current_price"]
        direction = message["direction"]
        sign = message["sign"]

        user = await UsersDAO.find_one_or_none(id=user_id)
        if not user:
            logger.warning(f"User {user_id} not found in notification service. Creating user record.")
            await UsersDAO.insert(id=user_id, email="")

        title = f"{direction} Изменение цены {asset_name}"
        
        message_text = (
            f"🚨 Значительное изменение цены!\n\n"
            f"**{asset_name} ({asset_symbol})** в вашем портфолио:\n"
            f"{direction} {sign}{change_percent}%\n"
            f"💰 Текущая цена: ${current_price:,.2f}"
        )

        await NotificationsDAO.insert(
            user_id=user_id,
            title=title,
            message=message_text,
            notification_type="price_alert"
        )
        
        logger.info(f"Price alert notification created for user {user_id}, asset {asset_name} ({change_percent:+.1f}%)")
        
    except Exception as e:
        logger.error(f"Error handling price change alert: {e}")



