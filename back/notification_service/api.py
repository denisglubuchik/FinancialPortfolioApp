import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from datetime import datetime

from back.notification_service.db.dao import NotificationsDAO

logger = logging.getLogger(__name__)


class UserResponse(BaseModel):
    id: int
    email: str
    telegram_id: Optional[int] = None

    class Config:
        from_attributes = True


class NotificationResponse(BaseModel):
    id: int
    user_id: int
    title: str
    message: str
    notification_type: str
    created_at: datetime
    delivery_status: str
    sent_at: Optional[datetime] = None
    retry_count: int
    user: UserResponse

    class Config:
        from_attributes = True


class DeliveryStatusUpdate(BaseModel):
    status: str


notification_router = APIRouter(
    prefix="/notifications"
)


@notification_router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "notification_api"}


@notification_router.get("/pending/telegram", response_model=List[NotificationResponse])
async def get_pending_telegram_notifications(limit: int = 50):
    """Get pending notifications for Telegram delivery"""
    logger.debug(f"Fetching pending Telegram notifications, limit: {limit}")
    
    try:
        notifications = await NotificationsDAO.get_pending_telegram_notifications(limit=limit)
        logger.info(f"Retrieved {len(notifications)} pending Telegram notifications")
        return notifications
    except Exception as e:
        logger.error(f"Failed to fetch pending Telegram notifications: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch notifications: {str(e)}"
        )


@notification_router.put("/{notification_id}/mark_sent")
async def mark_notification_sent(notification_id: int):
    """Mark notification as successfully sent"""
    logger.info(f"Marking notification as sent: notification_id={notification_id}")
    
    try:
        notification = await NotificationsDAO.mark_as_sent(notification_id)
        if not notification:
            logger.warning(f"Attempted to mark non-existent notification as sent: notification_id={notification_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )
        
        logger.info(f"Notification marked as sent successfully: notification_id={notification_id}")
        return {"status": "success", "message": "Notification marked as sent"}
    except Exception as e:
        logger.error(f"Failed to mark notification as sent, notification_id={notification_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update notification: {str(e)}"
        )


@notification_router.put("/{notification_id}/mark_failed")
async def mark_notification_failed(notification_id: int):
    """Mark notification as failed"""
    logger.warning(f"Marking notification as failed: notification_id={notification_id}")
    
    try:
        notification = await NotificationsDAO.mark_as_failed(notification_id)
        if not notification:
            logger.warning(f"Attempted to mark non-existent notification as failed: notification_id={notification_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )
        
        logger.warning(f"Notification marked as failed: notification_id={notification_id}, retry_count={notification.retry_count}")
        return {
            "status": "success", 
            "message": "Notification marked as failed",
            "retry_count": notification.retry_count,
            "delivery_status": notification.delivery_status
        }
    except Exception as e:
        logger.error(f"Failed to mark notification as failed, notification_id={notification_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update notification: {str(e)}"
        )


@notification_router.put("/{notification_id}/mark_skipped")
async def mark_notification_skipped(notification_id: int):
    """Mark notification as skipped (e.g., user blocked bot)"""
    logger.info(f"Marking notification as skipped: notification_id={notification_id}")
    
    try:
        notification = await NotificationsDAO.mark_as_skipped(notification_id)
        if not notification:
            logger.warning(f"Attempted to mark non-existent notification as skipped: notification_id={notification_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )
        
        logger.info(f"Notification marked as skipped: notification_id={notification_id}")
        return {"status": "success", "message": "Notification marked as skipped"}
    except Exception as e:
        logger.error(f"Failed to mark notification as skipped, notification_id={notification_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update notification: {str(e)}"
        )
    