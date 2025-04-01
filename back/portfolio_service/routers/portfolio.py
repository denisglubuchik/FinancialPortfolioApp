from fastapi import APIRouter

from back.portfolio_service.exceptions import PortfolioDoesntExistException, PortfolioAlreadyExistException
from back.portfolio_service.schemas.portfolio import SPortfolio, SPortfolioCreate
from back.portfolio_service.dependencies import UOWDep
from back.portfolio_service.services.portfolio import PortfolioService

router = APIRouter(
    prefix="/portfolio",
    tags=["portfolio"],
)


@router.post("/")
async def add_portfolio(new_portfolio: SPortfolioCreate, uow: UOWDep) -> int:
    portfolio = await PortfolioService().get_portfolio(uow, user_id=new_portfolio.user_id)
    if portfolio:
        raise PortfolioAlreadyExistException()
    portfolio_id = await PortfolioService().add_portfolio(uow, new_portfolio)
    return portfolio_id


@router.get("/{portfolio_id}")
async def get_portfolio(portfolio_id: int, uow: UOWDep) -> SPortfolio:
    portfolio = await PortfolioService().get_portfolio_by_id(uow, portfolio_id)
    if not portfolio:
        raise PortfolioDoesntExistException()
    return portfolio


@router.get("/by_user_id/{user_id}")
async def get_portfolio_by_user_id(user_id: int, uow: UOWDep) -> SPortfolio:
    portfolio = await PortfolioService().get_portfolio(uow, user_id=user_id)
    if not portfolio:
        raise PortfolioDoesntExistException()
    return portfolio


@router.delete("/{portfolio_id}")
async def delete_portfolio(portfolio_id: int, uow: UOWDep):
    portfolio = await PortfolioService().get_portfolio_by_id(uow, portfolio_id)
    if not portfolio:
        raise PortfolioDoesntExistException()
    await PortfolioService().delete_portfolio(uow, portfolio_id)
