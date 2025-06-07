from fastapi import APIRouter, HTTPException, Depends
from typing import List

from back.gateway.service import ServiceClient

# Service configuration
SERVICES = {
    "notification": "http://notification_app:8002",
}

# Router
router = APIRouter(
    prefix="/notifications",
    tags=["notifications"],
)


async def get_service_client() -> ServiceClient:
    """Dependency for service client injection"""
    client = ServiceClient(SERVICES)
    try:
        yield client
    finally:
        await client.close()


@router.get("/telegram/pending")
async def get_pending_telegram_notifications(
    limit: int = 50,
    client: ServiceClient = Depends(get_service_client)
):
    """Get pending notifications for Telegram delivery"""
    try:
        response = await client.get(
            service="notification",
            endpoint="/notifications/pending/telegram",
            params={"limit": limit}
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch notifications: {str(e)}")


@router.put("/telegram/{notification_id}/mark_sent")
async def mark_telegram_notification_sent(
    notification_id: int,
    client: ServiceClient = Depends(get_service_client)
):
    """Mark Telegram notification as sent"""
    try:
        response = await client.put(
            service="notification",
            endpoint=f"/notifications/{notification_id}/mark_sent"
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update notification: {str(e)}")


@router.put("/telegram/{notification_id}/mark_failed")
async def mark_telegram_notification_failed(
    notification_id: int,
    client: ServiceClient = Depends(get_service_client)
):
    """Mark Telegram notification as failed"""
    try:
        response = await client.put(
            service="notification",
            endpoint=f"/notifications/{notification_id}/mark_failed"
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update notification: {str(e)}")


@router.put("/telegram/{notification_id}/mark_skipped")
async def mark_telegram_notification_skipped(
    notification_id: int,
    client: ServiceClient = Depends(get_service_client)
):
    """Mark Telegram notification as skipped"""
    try:
        response = await client.put(
            service="notification",
            endpoint=f"/notifications/{notification_id}/mark_skipped"
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update notification: {str(e)}") 