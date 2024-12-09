from fastapi import APIRouter, Depends

from back.portfolio_service.dependencies import UOWDep, user_owns_portfolio, user_owns_transaction
from back.portfolio_service.schemas.transactions import STransaction, STransactionCreate
from back.portfolio_service.services.transactions import TransactionsService

router = APIRouter(
    prefix="/transactions",
    tags=["transactions"],
)


@router.post("/")
async def add_transaction(
        transaction: STransactionCreate,
        uow: UOWDep,
        portfolio_id: int = Depends(user_owns_portfolio),
):
    if portfolio_id:
        trans_id = await TransactionsService().add_transaction(portfolio_id, uow, transaction)
        return trans_id


@router.get("/")
async def get_transactions(
        uow: UOWDep,
        portfolio_id: int = Depends(user_owns_portfolio),
) -> list[STransaction]:
    transactions = await TransactionsService().get_all_transactions(uow, portfolio_id)
    return transactions


@router.get("/{transaction_id}")
async def get_transaction(
        transaction: STransaction = Depends(user_owns_transaction),
) -> STransaction:
    return transaction


@router.delete("/{transaction_id}")
async def delete_transaction(
        uow: UOWDep,
        transaction: STransaction = Depends(user_owns_transaction),
):
    await TransactionsService().delete_transaction(uow, transaction.id)


