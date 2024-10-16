from fastapi import APIRouter

from back.portfolio_service.dependencies import UOWDep
from back.portfolio_service.exceptions import AssetAlreadyExistException, AssetDoesntExistException
from back.portfolio_service.schemas.assets import SAsset, SAssetCreate
from back.portfolio_service.services.assets import AssetsService

router = APIRouter(
    prefix="/assets",
    tags=["assets"],
)


@router.post("/")
async def add_asset(asset: SAssetCreate, uow: UOWDep):
    asset = await AssetsService().get_asset(uow, asset.id)
    if asset:
        raise AssetAlreadyExistException()
    await AssetsService().add_asset(uow, asset)


@router.get("/")
async def get_assets(uow: UOWDep) -> list[SAsset]:
    assets = await AssetsService().get_all_assets(uow)
    return assets


@router.get("/{asset_id}")
async def get_asset(asset_id: int, uow: UOWDep) -> SAsset:
    asset = await AssetsService().get_asset(uow, asset_id)
    if not asset:
        raise AssetDoesntExistException()
    return asset


@router.delete("/{asset_id}")
async def delete_asset(asset_id: int, uow: UOWDep):
    await AssetsService().delete_asset(uow, asset_id)
