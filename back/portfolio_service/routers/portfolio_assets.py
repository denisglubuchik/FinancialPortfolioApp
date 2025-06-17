import logging
from fastapi import APIRouter, Depends

from back.portfolio_service.dependencies import UOWDep, user_owns_portfolio
from back.portfolio_service.exceptions import PortfolioAssetDoesntExistException
from back.portfolio_service.schemas.portfolio_assets import SPortfolioAsset, SPortfolioAssetMarketData
from back.portfolio_service.services.portfolio_assets import PortfolioAssetsService

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/portfolio_assets",
    tags=["portfolio_assets"],
)


@router.get("/{portfolio_id}")
async def get_portfolio_assets(uow: UOWDep, portfolio_id: int = Depends(user_owns_portfolio)) -> list[SPortfolioAssetMarketData]:
    logger.debug(f"Fetching all assets for portfolio_id: {portfolio_id}")
    
    try:
        portfolio_assets = await PortfolioAssetsService().get_all_portfolio_assets(uow, portfolio_id)
        logger.debug(f"Found {len(portfolio_assets)} assets in portfolio_id: {portfolio_id}")
        return portfolio_assets
    except Exception as e:
        logger.error(f"Failed to fetch portfolio assets for portfolio_id {portfolio_id}: {e}")
        raise


@router.get("/{portfolio_id}/{portfolio_asset_id}")
async def get_portfolio_asset(portfolio_asset_id: int, uow: UOWDep, portfolio_id: int = Depends(user_owns_portfolio)) -> SPortfolioAssetMarketData:
    logger.debug(f"Fetching portfolio asset: asset_id={portfolio_asset_id}, portfolio_id={portfolio_id}")
    
    portfolio_asset = await PortfolioAssetsService().get_portfolio_asset(uow, portfolio_asset_id)
    if not portfolio_asset:
        logger.warning(f"Portfolio asset not found: asset_id={portfolio_asset_id}")
        raise PortfolioAssetDoesntExistException()
    
    logger.debug(f"Portfolio asset found: asset_id={portfolio_asset_id}")
    return portfolio_asset


@router.delete("/{portfolio_id}/{portfolio_asset_id}")
async def delete_portfolio_asset(portfolio_asset_id: int, uow: UOWDep, portfolio_id: int = Depends(user_owns_portfolio)):
    logger.info(f"Deleting portfolio asset: asset_id={portfolio_asset_id}, portfolio_id={portfolio_id}")
    
    try:
        await PortfolioAssetsService().delete_portfolio_asset(uow, portfolio_asset_id)
        logger.info(f"Portfolio asset deleted successfully: asset_id={portfolio_asset_id}")
    except Exception as e:
        logger.error(f"Failed to delete portfolio asset {portfolio_asset_id}: {e}")
        raise
