from back.portfolio_service.exceptions import PortfolioAssetDoesntExistCannotSellException, \
    TransactionDoesntExistsException, TransactionCannotConductException
from back.portfolio_service.schemas.transactions import STransactionCreate, TransactionType
from back.portfolio_service.schemas.portfolio_assets import SPortfolioAssetCreate, SPortfolioAssetUpdate
from back.portfolio_service.utils.uow import IUnitOfWork


class TransactionsService:
    async def add_transaction(self, portfolio_id: int, uow: IUnitOfWork, transaction: STransactionCreate):
        async with uow:
            trans_dict = transaction.model_dump()
            trans_dict["portfolio_id"] = portfolio_id
            transaction_id = await uow.transactions.add(trans_dict)
            portfolio_asset = await uow.portfolio_assets.get_one(portfolio_id=portfolio_id,
                                                       asset_id=transaction.asset_id)
            portfolio = await uow.portfolio.get_one(id=portfolio_id)

            if portfolio_asset:
                if transaction.transaction_type == TransactionType.buy:
                    new_portfolio_asset = SPortfolioAssetUpdate(
                        portfolio_id=portfolio_id,
                        asset_id=transaction.asset_id,
                        quantity=portfolio_asset.quantity + transaction.quantity
                    )
                    total_invested = portfolio.total_invested + (transaction.price * transaction.quantity)
                    await uow.portfolio_assets.update(portfolio_asset.id, new_portfolio_asset.model_dump())
                elif transaction.transaction_type == TransactionType.sell:
                    if transaction.quantity > portfolio_asset.quantity:
                        raise TransactionCannotConductException()

                    elif transaction.quantity == portfolio_asset.quantity:
                        await uow.portfolio_assets.delete(portfolio_asset.id)
                        total_invested = portfolio.total_invested - (transaction.price * transaction.quantity)

                    else:
                        new_portfolio_asset = SPortfolioAssetUpdate(
                            portfolio_id=portfolio_id,
                            asset_id=transaction.asset_id,
                            quantity=portfolio_asset.quantity - transaction.quantity
                        )
                        total_invested = portfolio.total_invested - (transaction.price * transaction.quantity)
                        await uow.portfolio_assets.update(portfolio_asset.id, new_portfolio_asset.model_dump())
            else:
                if transaction.transaction_type == TransactionType.buy:
                    new_portfolio_asset = SPortfolioAssetCreate(
                        portfolio_id=portfolio_id,
                        asset_id=transaction.asset_id,
                        quantity=transaction.quantity
                    )
                    total_invested = portfolio.total_invested + (transaction.price * transaction.quantity)
                else:
                    raise PortfolioAssetDoesntExistCannotSellException()
                await uow.portfolio_assets.add(new_portfolio_asset.model_dump())

            await uow.portfolio.update(portfolio_id,
                                       {'total_invested': total_invested})
            await uow.commit()
            return transaction_id

    async def get_transaction(self, uow: IUnitOfWork, transaction_id: int):
        async with uow:
            transaction = await uow.transactions.get_one(id=transaction_id)
            return transaction

    async def get_all_transactions(self, uow: IUnitOfWork, portfolio_id: int, **kwargs):
        async with uow:
            transactions = await uow.transactions.get_all(portfolio_id=portfolio_id, **kwargs)
            return transactions

    async def delete_transaction(self, uow: IUnitOfWork, transaction_id: int):
        async with uow:
            transaction = await uow.transactions.get_one(id=transaction_id)
            if not transaction:
                raise TransactionDoesntExistsException()

            portfolio_asset = await uow.portfolio_assets.get_one(portfolio_id=transaction.portfolio_id,
                                                       asset_id=transaction.asset_id)
            if portfolio_asset:
                new_portfolio_asset = SPortfolioAssetUpdate(
                    portfolio_id=transaction.portfolio_id,
                    asset_id=transaction.asset_id,
                    quantity=portfolio_asset.quantity - transaction.quantity
                )
                await uow.portfolio_assets.update(portfolio_asset.id, new_portfolio_asset.model_dump())
            else:
                raise PortfolioAssetDoesntExistCannotSellException()

            portfolio = await uow.portfolio.get_one(id=transaction.portfolio_id)
            total_invested = portfolio.total_invested - (transaction.price * transaction.quantity)
            await uow.portfolio.update(transaction.portfolio_id,
                                       {'total_invested': total_invested})

            await uow.transactions.delete(transaction_id)
            await uow.commit()