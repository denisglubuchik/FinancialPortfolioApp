from sqlalchemy import select
from sqlalchemy.orm import aliased

from back.portfolio_service.repositories.base import SQLAlchemyRepository
from back.portfolio_service.models.portfolio_assets import PortfolioAssets
from back.portfolio_service.models.assets import Assets
from back.portfolio_service.models.portfolio import Portfolio


class PortfolioAssetsRepository(SQLAlchemyRepository):
    model = PortfolioAssets

    async def get_one(self, portfolio_id: int, asset_id: int):
        pa = aliased(PortfolioAssets)
        a = aliased(Assets)

        query = (
            select(
                pa.id, pa.asset_id, a.name, a.symbol, a.asset_type, pa.quantity
            )
            .select_from(pa)
            .join(a, pa.asset_id == a.id)
            .where(pa.asset_id == asset_id and pa.portfolio_id == portfolio_id)
        )
        res = await self.session.execute(query)
        return res.mappings().first()

    async def get_all_portfolio_assets(self, portfolio_id: int):
        pa = aliased(PortfolioAssets)
        a = aliased(Assets)

        query = (
            select(
                pa.id, pa.asset_id, a.name, a.symbol, a.asset_type, pa.quantity
            )
            .select_from(pa)
            .join(a, pa.asset_id == a.id)
            .where(pa.portfolio_id == portfolio_id)
        )

        res = await self.session.execute(query)
        return [dict(row) for row in res.mappings().all()]

    async def get_unique_asset_names_with_quantity(self):
        """Получает список уникальных имен активов из всех портфолио где quantity > 0"""
        query = (
            select(Assets.name)
            .select_from(Assets)
            .join(PortfolioAssets, Assets.id == PortfolioAssets.asset_id)
            .where(PortfolioAssets.quantity > 0)
            .distinct()
        )
        
        res = await self.session.execute(query)
        return [row.name for row in res.all()]
    
    async def get_users_with_asset(self, asset_name: str):
        """Получает список user_id пользователей, у которых есть конкретный актив"""
        query = (
            select(Portfolio.user_id)
            .select_from(Portfolio)
            .join(PortfolioAssets, Portfolio.id == PortfolioAssets.portfolio_id)
            .join(Assets, PortfolioAssets.asset_id == Assets.id)
            .where(
                Assets.name == asset_name,
                PortfolioAssets.quantity > 0
            )
            .distinct()
        )
        
        res = await self.session.execute(query)
        return [row.user_id for row in res.all()]
