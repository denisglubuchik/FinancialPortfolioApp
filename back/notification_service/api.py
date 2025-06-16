from typing import List, Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from datetime import datetime

from back.notification_service.db.dao import NotificationsDAO


# Pydantic schemas
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


# FastAPI app
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
    try:
        notifications = await NotificationsDAO.get_pending_telegram_notifications(limit=limit)
        return notifications
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch notifications: {str(e)}"
        )


@notification_router.put("/{notification_id}/mark_sent")
async def mark_notification_sent(notification_id: int):
    """Mark notification as successfully sent"""
    try:
        notification = await NotificationsDAO.mark_as_sent(notification_id)
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )
        return {"status": "success", "message": "Notification marked as sent"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update notification: {str(e)}"
        )


@notification_router.put("/{notification_id}/mark_failed")
async def mark_notification_failed(notification_id: int):
    """Mark notification as failed"""
    try:
        notification = await NotificationsDAO.mark_as_failed(notification_id)
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )
        return {
            "status": "success", 
            "message": "Notification marked as failed",
            "retry_count": notification.retry_count,
            "delivery_status": notification.delivery_status
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update notification: {str(e)}"
        )


@notification_router.put("/{notification_id}/mark_skipped")
async def mark_notification_skipped(notification_id: int):
    """Mark notification as skipped (e.g., user blocked bot)"""
    try:
        notification = await NotificationsDAO.mark_as_skipped(notification_id)
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )
        return {"status": "success", "message": "Notification marked as skipped"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update notification: {str(e)}"
        )
    