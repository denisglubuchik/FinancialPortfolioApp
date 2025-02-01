from fastapi import APIRouter, Depends

from back.portfolio_service.dependencies import UOWDep, user_owns_portfolio
from back.portfolio_service.exceptions import PortfolioAssetDoesntExistException
from back.portfolio_service.schemas.portfolio_assets import SPortfolioAsset, SPortfolioAssetMarketData
from back.portfolio_service.services.portfolio_assets import PortfolioAssetsService

router = APIRouter(
    prefix="/portfolio_assets",
    tags=["portfolio_assets"],
)


@router.get("/{portfolio_id}")
async def get_portfolio_assets(uow: UOWDep, portfolio_id: int = Depends(user_owns_portfolio)) -> list[SPortfolioAssetMarketData]:
    portfolio_assets = await PortfolioAssetsService().get_all_portfolio_assets(uow, portfolio_id)
    return portfolio_assets


@router.get("/{portfolio_id}/{portfolio_asset_id}")
async def get_portfolio_asset(portfolio_asset_id: int, uow: UOWDep, portfolio_id: int = Depends(user_owns_portfolio)) -> SPortfolioAssetMarketData:
    portfolio_asset = await PortfolioAssetsService().get_portfolio_asset(uow, portfolio_asset_id)
    if not portfolio_asset:
        raise PortfolioAssetDoesntExistException()
    return portfolio_asset


@router.delete("/{portfolio_id}/{portfolio_asset_id}")
async def delete_portfolio_asset(portfolio_asset_id: int, uow: UOWDep, portfolio_id: int = Depends(user_owns_portfolio)):
    await PortfolioAssetsService().delete_portfolio_asset(uow, portfolio_asset_id)
