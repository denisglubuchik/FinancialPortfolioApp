from sqlalchemy import select
from sqlalchemy.orm import aliased

from back.portfolio_service.repositories.base import SQLAlchemyRepository
from back.portfolio_service.models.portfolio_assets import PortfolioAssets
from back.portfolio_service.models.assets import Assets


class PortfolioAssetsRepository(SQLAlchemyRepository):
    model = PortfolioAssets

    async def get_one(self, asset_id: int):
        pa = aliased(PortfolioAssets)
        a = aliased(Assets)

        query = (
            select(
                pa.id, pa.asset_id, a.name, a.symbol, a.asset_type, pa.quantity
            )
            .select_from(pa)
            .join(a, pa.asset_id == a.id)
            .where(pa.asset_id == asset_id)
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
