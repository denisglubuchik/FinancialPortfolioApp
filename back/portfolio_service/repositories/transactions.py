from sqlalchemy import select

from back.portfolio_service.models.portfolio_assets import PortfolioAssets
from back.portfolio_service.repositories.base import SQLAlchemyRepository
from back.portfolio_service.models.transactions import Transactions


class TransactionsRepository(SQLAlchemyRepository):
    model = Transactions

    async def get_all_transactions_for_portfolio_asset(self, portfolio_id: int, portfolio_asset_id: int):
        query = select(self.model).join(PortfolioAssets, self.model.portfolio_id == PortfolioAssets.portfolio_id).filter_by(portfolio_id=portfolio_id, id=portfolio_asset_id)
        res = await self.session.execute(query)
        return [model.read_model() for model in res.scalars().all()]
