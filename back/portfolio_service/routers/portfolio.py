from fastapi import APIRouter

from back.portfolio_service.schemas.portfolio import SPortfolio, SPortfolioCreate
from back.portfolio_service.dependencies import UOWDep
from back.portfolio_service.services.portfolio import PortfolioService

router = APIRouter(
    prefix="/portfolio",
    tags=["portfolio"],
)


@router.post("/")
async def add_portfolio(portfolio: SPortfolioCreate, uow: UOWDep) -> int:
    portfolio_id = await PortfolioService().add_portfolio(uow, portfolio)
    return portfolio_id


@router.get("/{portfolio_id}")
async def get_portfolio(portfolio_id: int, uow: UOWDep) -> SPortfolio:
    portfolio = await PortfolioService().get_portfolio(uow, portfolio_id)
    return portfolio
