import logging
from fastapi import APIRouter

from back.portfolio_service.exceptions import PortfolioDoesntExistException, PortfolioAlreadyExistException
from back.portfolio_service.schemas.portfolio import SPortfolio, SPortfolioCreate
from back.portfolio_service.dependencies import UOWDep
from back.portfolio_service.services.portfolio import PortfolioService

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/portfolio",
    tags=["portfolio"],
)


@router.post("/")
async def add_portfolio(new_portfolio: SPortfolioCreate, uow: UOWDep) -> int:
    logger.info(f"Creating portfolio for user_id: {new_portfolio.user_id}")
    
    portfolio = await PortfolioService().get_portfolio(uow, user_id=new_portfolio.user_id)
    if portfolio:
        logger.warning(f"Portfolio creation failed: already exists for user_id: {new_portfolio.user_id}")
        raise PortfolioAlreadyExistException()
    
    try:
        portfolio_id = await PortfolioService().add_portfolio(uow, new_portfolio)
        logger.info(f"Portfolio created successfully: portfolio_id={portfolio_id}, user_id={new_portfolio.user_id}")
        return portfolio_id
    except Exception as e:
        logger.error(f"Portfolio creation failed for user_id {new_portfolio.user_id}: {e}")
        raise


@router.get("/{portfolio_id}")
async def get_portfolio(portfolio_id: int, uow: UOWDep) -> SPortfolio:
    portfolio = await PortfolioService().get_portfolio_by_id(uow, portfolio_id)
    if not portfolio:
        logger.warning(f"Portfolio not found: portfolio_id={portfolio_id}")
        raise PortfolioDoesntExistException()
    
    return portfolio


@router.get("/by_user_id/{user_id}")
async def get_portfolio_by_user_id(user_id: int, uow: UOWDep) -> SPortfolio:
    portfolio = await PortfolioService().get_portfolio(uow, user_id=user_id)
    if not portfolio:
        logger.warning(f"Portfolio not found for user_id: {user_id}")
        raise PortfolioDoesntExistException()
    
    return portfolio


@router.delete("/{portfolio_id}")
async def delete_portfolio(portfolio_id: int, uow: UOWDep):
    portfolio = await PortfolioService().get_portfolio_by_id(uow, portfolio_id)
    if not portfolio:
        logger.warning(f"Portfolio deletion failed: not found portfolio_id={portfolio_id}")
        raise PortfolioDoesntExistException()
    
    try:
        await PortfolioService().delete_portfolio(uow, portfolio_id)
        logger.info(f"Portfolio deleted successfully: portfolio_id={portfolio_id}")
    except Exception as e:
        logger.error(f"Portfolio deletion failed for portfolio_id {portfolio_id}: {e}")
        raise
