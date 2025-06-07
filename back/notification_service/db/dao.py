from datetime import datetime
from sqlalchemy import select, insert, update, delete, and_, func
from sqlalchemy.orm import joinedload

from back.notification_service.db.database import async_session_maker
from back.notification_service.db.models import Users, Notifications, DeliveryStatus


class BaseDAO:
    model = None

    @classmethod
    async def find_by_id(cls, model_id: int):
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(id=model_id)
            res = await session.execute(query)
            return res.scalar_one_or_none()

    @classmethod
    async def find_one_or_none(cls, **filter_by):
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(**filter_by)
            res = await session.execute(query)
            return res.scalar_one_or_none()

    @classmethod
    async def find_all(cls, **filter_by):
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(**filter_by)
            res = await session.execute(query)
            return res.scalars().all()

    @classmethod
    async def insert(cls, **data):
        async with async_session_maker() as session:
            query = insert(cls.model).values(**data).returning(cls.model)
            res = await session.execute(query)
            await session.commit()
            return res.scalar_one_or_none()

    @classmethod
    async def update(cls, model_id: int, **data):
        async with async_session_maker() as session:
            query = update(cls.model).filter_by(id=model_id).values(**data).returning(cls.model)
            res = await session.execute(query)
            await session.commit()
            return res.scalar_one_or_none()

    @classmethod
    async def delete(cls, model_id: int):
        async with async_session_maker() as session:
            query = delete(cls.model).filter_by(id=model_id)
            await session.execute(query)
            await session.commit()


class UsersDAO(BaseDAO):
    model = Users

    @classmethod
    async def find_by_telegram_id(cls, telegram_id: int):
        """Find user by Telegram ID"""
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(telegram_id=telegram_id)
            res = await session.execute(query)
            return res.scalar_one_or_none()

    @classmethod
    async def update_telegram_id(cls, user_id: int, telegram_id: int):
        """Update user's Telegram ID"""
        return await cls.update(user_id, telegram_id=telegram_id)


class NotificationsDAO(BaseDAO):
    model = Notifications

    @classmethod
    async def get_pending_telegram_notifications(cls, limit: int = 50):
        """Get pending notifications for users with Telegram IDs"""
        async with async_session_maker() as session:
            query = (
                select(cls.model)
                .options(joinedload(cls.model.user))
                .join(Users)
                .filter(
                    and_(
                        cls.model.delivery_status == DeliveryStatus.PENDING,
                        Users.telegram_id.isnot(None),
                        cls.model.retry_count < 3 
                    )
                )
                .order_by(cls.model.created_at)
                .limit(limit)
            )
            res = await session.execute(query)
            return res.scalars().all()

    @classmethod
    async def mark_as_sent(cls, notification_id: int):
        """Mark notification as successfully sent"""
        return await cls.update(
            notification_id, 
            delivery_status=DeliveryStatus.SENT,
            sent_at=func.now()
        )

    @classmethod
    async def mark_as_failed(cls, notification_id: int):
        """Mark notification as failed and increment retry count"""
        async with async_session_maker() as session:
            # First get current retry count
            notification = await cls.find_by_id(notification_id)
            if not notification:
                return None
            
            new_retry_count = notification.retry_count + 1
            new_status = DeliveryStatus.FAILED if new_retry_count >= 3 else DeliveryStatus.PENDING
            
            query = (
                update(cls.model)
                .filter_by(id=notification_id)
                .values(
                    delivery_status=new_status,
                    retry_count=new_retry_count
                )
                .returning(cls.model)
            )
            res = await session.execute(query)
            await session.commit()
            return res.scalar_one_or_none()

    @classmethod
    async def mark_as_skipped(cls, notification_id: int):
        """Mark notification as skipped (e.g., user blocked bot)"""
        return await cls.update(
            notification_id,
            delivery_status=DeliveryStatus.SKIPPED,
            sent_at=func.now()
        )


