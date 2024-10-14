from back.portfolio_service.utils.uow import IUnitOfWork


class PortfolioAssetsService:
    async def get_portfolio_asset(self, uow: IUnitOfWork, portfolio_id: int, asset_id: int):
        async with uow:
            asset = await uow.portfolio_assets.get_one(portfolio_id=portfolio_id, asset_id=asset_id)
            return asset

    async def get_all_portfolio_assets(self, uow: IUnitOfWork, portfolio_id: int):
        async with uow:
            assets = await uow.portfolio_assets.get_all(portfolio_id=portfolio_id)
            return assets

    async def delete_portfolio_asset(self, uow: IUnitOfWork, portfolio_id: int, asset_id: int):
        async with uow:
            await uow.portfolio_assets.delete(portfolio_id, asset_id)
            await uow.commit()
