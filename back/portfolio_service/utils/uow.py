from abc import ABC, abstractmethod
from typing import Type

from back.portfolio_service.database import async_session_maker
from back.portfolio_service.repositories.assets import AssetsRepository
from back.portfolio_service.repositories.portfolio import PortfolioRepository
from back.portfolio_service.repositories.portfolio_assets import PortfolioAssetsRepository
from back.portfolio_service.repositories.transactions import TransactionsRepository
from back.portfolio_service.repositories.users import UsersRepository


class IUnitOfWork(ABC):
    portfolio: Type[PortfolioRepository]
    assets: Type[AssetsRepository]
    portfolio_assets: Type[PortfolioAssetsRepository]
    transactions: Type[TransactionsRepository]
    users: Type[UsersRepository]

    @abstractmethod
    def __init__(self):
        ...

    @abstractmethod
    async def __aenter__(self):
        ...

    @abstractmethod
    async def __aexit__(self, *args):
        ...

    @abstractmethod
    async def commit(self):
        ...

    @abstractmethod
    async def rollback(self):
        ...


class UnitOfWork:
    def __init__(self):
        self.session_factory = async_session_maker

    async def __aenter__(self):
        self.session = self.session_factory()

        self.portfolio = PortfolioRepository(self.session)
        self.assets = AssetsRepository(self.session)
        self.portfolio_assets = PortfolioAssetsRepository(self.session)
        self.transactions = TransactionsRepository(self.session)
        self.users = UsersRepository(self.session)

    async def __aexit__(self, *args):
        await self.rollback()
        await self.session.close()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()
