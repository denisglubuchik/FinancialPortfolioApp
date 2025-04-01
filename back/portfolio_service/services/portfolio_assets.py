from back.portfolio_service.utils.uow import IUnitOfWork


class PortfolioAssetsService:
    async def get_portfolio_asset(self, uow: IUnitOfWork, asset_id: int):
        async with uow:
            asset = await uow.portfolio_assets.get_one(asset_id=asset_id)
            return asset

    async def get_all_portfolio_assets(self, uow: IUnitOfWork, portfolio_id: int):
        # TODO добавить получение текущих курсов из редиса
        async with uow:
            portfolio_assets = await uow.portfolio_assets.get_all_portfolio_assets(portfolio_id)

        assets = []
        for portfolio_asset in portfolio_assets:
            assets.append(portfolio_asset["name"])

        from back.portfolio_service.redis import redis_client
        await redis_client.connect()
        market_data = await redis_client.get_assets(assets)
        await redis_client.close()

        for portfolio_asset in portfolio_assets:
            portfolio_asset["current_price"] = float(market_data[portfolio_asset["name"]]["current_price"])
            portfolio_asset["usd_24h_change"] = market_data[portfolio_asset["name"]]["usd_24h_change"]
            portfolio_asset["last_updated"] = market_data[portfolio_asset["name"]]["last_updated"]

        return portfolio_assets

    async def delete_portfolio_asset(self, uow: IUnitOfWork, asset_id: int):
        async with uow:
            await uow.portfolio_assets.delete(asset_id)
            await uow.commit()
