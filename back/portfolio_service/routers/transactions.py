from fastapi import APIRouter

from back.portfolio_service.dependencies import UOWDep
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
async def get_transactions(portfolio_id: int, uow: UOWDep) -> list[STransaction]:
    transactions = await TransactionsService().get_all_transactions(uow, portfolio_id)
    return transactions


@router.get("/{transaction_id}")
async def get_transaction(portfolio_id: int, transaction_id: int, uow: UOWDep) -> STransaction:
    transaction = await TransactionsService().get_transaction(uow, transaction_id)
    return transaction


@router.delete("/{transaction_id}")
async def delete_transaction(transaction_id: int, uow: UOWDep):
    await TransactionsService().delete_transaction(uow, transaction_id)
