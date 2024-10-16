from sqlalchemy import func, DateTime, ForeignKey, Computed, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from back.portfolio_service.database import Base
from back.portfolio_service.schemas.transactions import STransaction, TransactionType


class Transactions(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True)
    portfolio_id: Mapped[int] = mapped_column(ForeignKey("portfolios.id", ondelete="CASCADE"))
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id"))
    transaction_type: Mapped[TransactionType] = mapped_column(Enum(TransactionType))
    quantity: Mapped[float]
    price: Mapped[int]
    total_price: Mapped[float] = mapped_column(Computed("quantity * price"))
    transaction_date = mapped_column(DateTime(timezone=True), default=func.now())

    portfolio: Mapped["Portfolio"] = relationship(back_populates="transactions")
    asset: Mapped["Assets"] = relationship(back_populates="transactions")

    def read_model(self) -> STransaction:
        return STransaction(
            id=self.id,
            portfolio_id=self.portfolio_id,
            asset_id=self.asset_id,
            transaction_type=self.transaction_type,
            quantity=self.quantity,
            price=self.price,
            total_price=self.total_price,
            transaction_date=self.transaction_date
        )
