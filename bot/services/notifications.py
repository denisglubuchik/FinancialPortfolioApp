import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from aiogram import Bot
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest, TelegramRetryAfter

from bot.core.config import settings
from bot.core.loader import bot
from bot.services.base import ServiceClient

logger = logging.getLogger(__name__)


async def get_pending_notifications(limit: int = 50) -> List[Dict[str, Any]]:
    """Get pending notifications from the API Gateway"""
    async with ServiceClient({"gateway": settings.gateway_url}) as client:
        try:
            response = await client.get(
                service="gateway",
                endpoint="/notifications/telegram/pending",
                params={"limit": limit}
            )
            logger.debug(f"API response type: {type(response)}, length: {len(response) if isinstance(response, (list, dict)) else 'N/A'}")
            result = response if isinstance(response, list) else []
            logger.debug(f"Returning {len(result)} notifications")
            return result
        except Exception as e:
            logger.error(f"Failed to fetch pending notifications: {e}")
            return []
            
async def mark_notification_sent(notification_id: int) -> bool:
    """Mark notification as successfully sent"""
    async with ServiceClient({"gateway": settings.gateway_url}) as client:
        try:
            await client.put(
                service="gateway",
                endpoint=f"/notifications/telegram/{notification_id}/mark_sent"
            )
            return True
        except Exception as e:
            logger.error(f"Failed to mark notification {notification_id} as sent: {e}")
            return False

async def mark_notification_failed(notification_id: int) -> bool:
    """Mark notification as failed"""
    async with ServiceClient({"gateway": settings.gateway_url}) as client:
        try:
            await client.put(
                service="gateway",
                endpoint=f"/notifications/telegram/{notification_id}/mark_failed"
            )
            return True
        except Exception as e:
            logger.error(f"Failed to mark notification {notification_id} as failed: {e}")
            return False
    

async def mark_notification_skipped(notification_id: int) -> bool:
    """Mark notification as skipped (e.g., user blocked bot)"""
    async with ServiceClient({"gateway": settings.gateway_url}) as client:
        try:
            await client.put(
                service="gateway",
                endpoint=f"/notifications/telegram/{notification_id}/mark_skipped"
            )
            return True
        except Exception as e:
            logger.error(f"Failed to mark notification {notification_id} as skipped: {e}")
            return False

async def send_notification_to_user(notification: Dict[str, Any]) -> bool:
    """Send a single notification to Telegram user"""
    async with ServiceClient({"gateway": settings.gateway_url}) as client:
        try:
            telegram_id = notification["user"]["telegram_id"]
            if not telegram_id:
                logger.warning(f"No Telegram ID for notification {notification['id']}")
                await mark_notification_skipped(notification["id"])
                return False

            message_text = _format_notification_message(notification)

            await bot.send_message(
                chat_id=telegram_id,
                text=message_text,
                parse_mode="HTML"
            )

            success = await mark_notification_sent(notification["id"])
            if success:
                logger.info(f"Successfully sent notification {notification['id']} to user {telegram_id}")
            return success

        except TelegramForbiddenError:
            logger.info(f"User {telegram_id} blocked the bot, skipping notification {notification['id']}")
            await mark_notification_skipped(notification["id"])
            return False

        except TelegramBadRequest as e:
            logger.warning(f"Bad request sending notification {notification['id']}: {e}")
            await mark_notification_skipped(notification["id"])
            return False

        except TelegramRetryAfter as e:
            logger.warning(f"Rate limited, will retry notification {notification['id']} later: {e}")
            await mark_notification_failed(notification["id"])
            return False

        except Exception as e:
            logger.error(f"Error sending notification {notification['id']}: {e}")
            await mark_notification_failed(notification["id"])
            return False

def _format_notification_message(notification: Dict[str, Any]) -> str:
    """Format notification for Telegram display"""
    title = notification.get("title", "Уведомление")
    message = notification.get("message", "")
    notification_type = notification.get("notification_type", "general")
    created_at = notification.get("created_at", "")

    if isinstance(created_at, str):
        try:
            created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            time_str = created_at.strftime("%d.%m.%Y %H:%M")
        except:
            time_str = created_at
    else:
        time_str = str(created_at)

    type_emoji = {
        "portfolio_update": "📊", 
        "price_alert": "💰",
        "transaction": "💳",
        "system": "⚙️",
        "general": "📢"
    }.get(notification_type, "📢")

    formatted_message = f"""
{type_emoji} <b>{title}</b>

{message}

<i>📅 {time_str}</i>
""".strip()

    return formatted_message

async def process_pending_notifications() -> Dict[str, int]:
    """Process all pending notifications and return statistics"""
    stats = {
        "fetched": 0,
        "sent": 0,
        "failed": 0,
        "skipped": 0
    }

    try:
        logger.debug("Fetching pending notifications from API...")
        notifications = await get_pending_notifications()
        stats["fetched"] = len(notifications)
        logger.info(f"Fetched {len(notifications)} pending notifications from API")

        if not notifications:
            logger.info("No pending notifications found")
            return stats

        logger.info(f"Processing {len(notifications)} pending notifications")

        # Process each notification
        for notification in notifications:
            success = await send_notification_to_user(notification)
            if success:
                stats["sent"] += 1
            else:
                # The specific failure type (failed/skipped) is already handled in send_notification_to_user
                pass

        logger.info(f"Notification processing complete: {stats}")

    except Exception as e:
        logger.error(f"Error processing notifications: {e}")

    return stats 