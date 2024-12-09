from typing import Annotated
from fastapi import Depends

from back.portfolio_service.exceptions import UserDoesntOwnPortfolioException, UserDoesntOwnTransactionException, \
    TransactionDoesntExistsException, PortfolioDoesntExistException
from back.portfolio_service.utils.uow import IUnitOfWork, UnitOfWork

UOWDep = Annotated[IUnitOfWork, Depends(UnitOfWork)]


async def user_owns_portfolio(user_id: int, portfolio_id: int, uow: UOWDep):
    async with uow:
        portfolio = await uow.portfolio.get_one(user_id=user_id)
    if not portfolio:
        raise PortfolioDoesntExistException()
    if portfolio.id != portfolio_id:
        raise UserDoesntOwnPortfolioException()
    return portfolio_id

async def user_owns_transaction(user_id: int, transaction_id: int, uow: UOWDep):
    async with uow:
        transaction = await uow.transactions.get_one(id=transaction_id)
        if not transaction:
            raise TransactionDoesntExistsException()

        portfolio = await uow.portfolio.get_one(id=transaction.portfolio_id)

    if portfolio.user_id != user_id:
        raise UserDoesntOwnTransactionException()
    return transaction
