import logging
from fastapi import APIRouter, Depends

from back.portfolio_service.dependencies import UOWDep, user_owns_portfolio, user_owns_transaction
from back.portfolio_service.schemas.transactions import STransaction, STransactionCreate
from back.portfolio_service.services.transactions import TransactionsService

logger = logging.getLogger(__name__)

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
        try:
            trans_id = await TransactionsService().add_transaction(portfolio_id, uow, transaction)
            logger.info(f"Transaction created successfully: transaction_id={trans_id}, portfolio_id={portfolio_id}")
            return trans_id
        except Exception as e:
            logger.error(f"Transaction creation failed for portfolio_id {portfolio_id}: {e}")
            raise


@router.get("/")
async def get_transactions(
        uow: UOWDep,
        portfolio_id: int = Depends(user_owns_portfolio),
        portfolio_asset_id: int = None
) -> list[STransaction]:
    try:
        transactions = await TransactionsService().get_all_transactions(uow, portfolio_id, asset_id=portfolio_asset_id)
        return transactions
    except Exception as e:
        logger.error(f"Failed to fetch transactions for portfolio_id {portfolio_id}: {e}")
        raise


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
    logger.info(f"Deleting transaction: transaction_id={transaction.id}")
    
    try:
        await TransactionsService().delete_transaction(uow, transaction.id)
        logger.info(f"Transaction deleted successfully: transaction_id={transaction.id}")
        return {"message": "Transaction deleted"}
    except Exception as e:
        logger.error(f"Transaction deletion failed for transaction_id {transaction.id}: {e}")
        raise

