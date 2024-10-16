from fastapi import APIRouter

from back.portfolio_service.dependencies import UOWDep
from back.portfolio_service.exceptions import AssetAlreadyExistException, AssetDoesntExistException
from back.portfolio_service.schemas.assets import SAsset, SAssetCreate, AssetType
from back.portfolio_service.services.assets import AssetsService

router = APIRouter(
    prefix="/assets",
    tags=["assets"],
)


@router.post("/")
async def add_asset(new_asset: SAssetCreate, uow: UOWDep):
    asset = await AssetsService().get_asset(uow, name=new_asset.name)
    if asset:
        raise AssetAlreadyExistException()
    asset_id = await AssetsService().add_asset(uow, new_asset)
    return asset_id


@router.get("/")
async def get_assets(uow: UOWDep, asset_type: AssetType = None) -> list[SAsset]:
    assets = await AssetsService().get_all_assets(uow, asset_type)
    return assets


@router.get("/{asset_id}")
async def get_asset(asset_id: int, uow: UOWDep) -> SAsset:
    asset = await AssetsService().get_asset_by_id(uow, asset_id)
    if not asset:
        raise AssetDoesntExistException()
    return asset


@router.delete("/{asset_id}")
async def delete_asset(asset_id: int, uow: UOWDep):
    asset = await AssetsService().get_asset_by_id(uow, asset_id)
    if not asset:
        raise AssetDoesntExistException()
    await AssetsService().delete_asset(uow, asset_id)
