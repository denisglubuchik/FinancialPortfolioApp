from back.portfolio_service.exceptions import UserDoesntExistException
from back.portfolio_service.schemas.portfolio import SPortfolioCreate, SPortfolioUpdate
from back.portfolio_service.utils.uow import IUnitOfWork


class PortfolioService:
    async def add_portfolio(self, uow: IUnitOfWork, portfolio: SPortfolioCreate):
        async with uow:
            user = await uow.users.get_one(id=portfolio.user_id)
            if not user:
                raise UserDoesntExistException()
            portfolio_id = await uow.portfolio.add(portfolio.model_dump())
            await uow.commit()
            return portfolio_id

    async def get_portfolio_by_id(self, uow: IUnitOfWork, portfolio_id: int):
        async with uow:
            portfolio = await uow.portfolio.get_one(id=portfolio_id)
            return portfolio

    async def get_portfolio(self, uow: IUnitOfWork, **kwargs):
        async with uow:
            portfolio = await uow.portfolio.get_one(**kwargs)
            return portfolio

    async def update_portfolio(self, uow: IUnitOfWork, portfolio_id: int, portfolio: SPortfolioUpdate):
        async with uow:
            await uow.portfolio.update(portfolio_id, portfolio.model_dump())
            await uow.commit()

    async def delete_portfolio(self, uow: IUnitOfWork, portfolio_id: int):
        async with uow:
            await uow.portfolio.delete(portfolio_id)
            await uow.commit()
