from back.portfolio_service.repositories.base import SQLAlchemyRepository
from back.portfolio_service.models.portfolio_assets import PortfolioAssets


class PortfolioAssetsRepository(SQLAlchemyRepository):
    model = PortfolioAssets
