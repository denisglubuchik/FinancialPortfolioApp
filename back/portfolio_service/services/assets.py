from back.portfolio_service.schemas.assets import SAssetCreate
from back.portfolio_service.utils.uow import IUnitOfWork


class AssetsService:
    async def add_asset(self, uow: IUnitOfWork, asset: SAssetCreate):
        async with uow:
            asset_id = await uow.assets.add(asset.model_dump())
            await uow.commit()
            return asset_id

    async def get_asset_by_id(self, uow: IUnitOfWork, asset_id: int):
        async with uow:
            asset = await uow.assets.get_one(id=asset_id)
            return asset

    async def get_asset(self, uow, **kwargs):
        async with uow:
            asset = await uow.assets.get_one(**kwargs)
            return asset

    async def get_all_assets(self, uow: IUnitOfWork, asset_type):
        async with uow:
            if asset_type:
                assets = await uow.assets.get_all(asset_type=asset_type)
            else:
                assets = await uow.assets.get_all()
            return assets

    async def delete_asset(self, uow: IUnitOfWork, asset_id: int):
        async with uow:
            await uow.assets.delete(asset_id)
            await uow.commit()