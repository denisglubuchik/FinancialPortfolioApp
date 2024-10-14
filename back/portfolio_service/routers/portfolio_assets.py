from fastapi import APIRouter

from back.portfolio_service.dependencies import UOWDep
from back.portfolio_service.schemas.portfolio_assets import SPortfolioAsset
from back.portfolio_service.services.portfolio_assets import PortfolioAssetsService

router = APIRouter(
    prefix="/portfolio_assets",
    tags=["portfolio_assets"],
)


@router.get("/{portfolio_id}")
async def get_portfolio_assets(portfolio_id: int, uow: UOWDep) -> list[SPortfolioAsset]:
    portfolio_assets = await PortfolioAssetsService().get_all_portfolio_assets(uow, portfolio_id)
    return portfolio_assets


@router.get("/{portfolio_id}/{asset_id}")
async def get_portfolio_asset(portfolio_id: int, asset_id: int, uow: UOWDep) -> SPortfolioAsset:
    portfolio_asset = await PortfolioAssetsService().get_portfolio_asset(uow, portfolio_id, asset_id)
    return portfolio_asset


@router.delete("/{portfolio_id}/{asset_id}")
async def delete_portfolio_asset(portfolio_id: int, asset_id: int, uow: UOWDep):
    await PortfolioAssetsService().delete_portfolio_asset(uow, portfolio_id, asset_id)
