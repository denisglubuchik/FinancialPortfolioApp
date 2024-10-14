from abc import ABC, abstractmethod

from sqlalchemy import insert, update, select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from back.portfolio_service.database import async_session_maker


class AbstractRepository(ABC):
    @abstractmethod
    async def add(self, **kwargs):
        raise NotImplementedError

    @abstractmethod
    async def update(self, **kwargs):
        raise NotImplementedError

    @abstractmethod
    async def delete(self, **kwargs):
        raise NotImplementedError

    @abstractmethod
    async def get_one(self, **kwargs):
        raise NotImplementedError

    @abstractmethod
    async def get_all(self, **kwargs):
        raise NotImplementedError


class SQLAlchemyRepository(AbstractRepository):
    model = None

    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, data: dict) -> int:
        stmt = insert(self.model).values(**data).returning(self.model.id)
        res = await self.session.execute(stmt)
        return res.scalar_one()

    async def update(self, id: int, data: dict):
        stmt = update(self.model).values(**data).filter_by(id=id).returning(self.model)
        res = await self.session.execute(stmt)
        return res.scalar_one()

    async def delete(self, id: int) -> None:
        stmt = delete(self.model).filter_by(id=id)
        await self.session.execute(stmt)

    async def get_one(self, **kwargs):
        query = select(self.model).filter_by(**kwargs)
        res = await self.session.execute(query)
        res = res.scalar_one_or_none()
        if res is None:
            return None
        return res.read_model()

    async def get_all(self, **kwargs):
        query = select(self.model).filter_by(**kwargs)
        res = await self.session.execute(query)
        return [model.read_model() for model in res.scalars().all()]
