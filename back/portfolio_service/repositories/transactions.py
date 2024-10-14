from back.portfolio_service.repositories.base import SQLAlchemyRepository
from back.portfolio_service.models.transactions import Transactions


class TransactionsRepository(SQLAlchemyRepository):
    model = Transactions
