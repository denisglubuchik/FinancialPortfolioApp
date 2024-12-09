from fastapi import APIRouter

from back.portfolio_service.dependencies import UOWDep
from back.portfolio_service.exceptions import UserDoesntOwnPortfolioException
from back.portfolio_service.schemas.transactions import STransaction, STransactionCreate
from back.portfolio_service.services.transactions import TransactionsService

router = APIRouter(
    prefix="/transactions",
    tags=["transactions"],
)


@router.post("/")
async def add_transaction(transaction: STransactionCreate, uow: UOWDep):
    trans_id = await TransactionsService().add_transaction(uow, transaction)
    return trans_id


@router.get("/")
async def get_transactions(portfolio_id: int, user_id: int, uow: UOWDep) -> list[STransaction]:
    await check_user_owns_portfolio(user_id, portfolio_id, uow)
    transactions = await TransactionsService().get_all_transactions(uow, portfolio_id)
    return transactions


@router.get("/{transaction_id}")
async def get_transaction(portfolio_id: int, transaction_id: int, uow: UOWDep) -> STransaction:
    transaction = await TransactionsService().get_transaction(uow, transaction_id)
    return transaction


@router.delete("/{transaction_id}")
async def delete_transaction(transaction_id: int, uow: UOWDep):
    await TransactionsService().delete_transaction(uow, transaction_id)


async def check_user_owns_portfolio(user_id: int, portfolio_id: int, uow: UOWDep):
    portfolio = await uow.portfolio.get_one(user_id=user_id)
    if portfolio.id != portfolio_id:
        raise UserDoesntOwnPortfolioException()