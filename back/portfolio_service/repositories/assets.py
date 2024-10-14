from back.portfolio_service.repositories.base import SQLAlchemyRepository
from back.portfolio_service.models.assets import Assets


class AssetsRepository(SQLAlchemyRepository):
    model = Assets
