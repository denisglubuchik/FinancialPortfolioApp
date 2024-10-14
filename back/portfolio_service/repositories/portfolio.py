from back.portfolio_service.repositories.base import SQLAlchemyRepository
from back.portfolio_service.models.portfolio import Portfolio


class PortfolioRepository(SQLAlchemyRepository):
    model = Portfolio
