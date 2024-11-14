from sqlalchemy import select, insert, update, delete

from back.user_service.db.database import async_session_maker
from back.user_service.db.models import Users, VerificationTokens


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
    async def update_password(cls, user_id: int, hashed_password):
        async with async_session_maker() as session:
            query = update(cls.model).filter_by(id=user_id).values(hashed_password=hashed_password).returning(cls.model)
            await session.execute(query)
            await session.commit()


class VerificationTokensDAO(BaseDAO):
    model = VerificationTokens
