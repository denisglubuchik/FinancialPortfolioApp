"""price converted to float from int

Revision ID: 25111fc37b2d
Revises: 79b171bbac79
Create Date: 2025-04-01 12:46:59.442686

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '25111fc37b2d'
down_revision: Union[str, None] = '79b171bbac79'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop the generated column
    op.drop_column('transactions', 'total_price')

    # Alter the column type
    op.alter_column('transactions', 'price',
               existing_type=sa.INTEGER(),
               type_=sa.Float(),
               existing_nullable=False)

    # Recreate the generated column
    op.add_column('transactions',
                  sa.Column('total_price',
                            sa.Float(),
                            sa.Computed('price * quantity', persisted=True))
                 )


def downgrade() -> None:
    # Drop the generated column
    op.drop_column('transactions', 'total_price')

    # Revert the column type
    op.alter_column('transactions', 'price',
               existing_type=sa.Float(),
               type_=sa.INTEGER(),
               existing_nullable=False)

    # Recreate the generated column with its original definition
    op.add_column('transactions',
                  sa.Column('total_price',
                            sa.INTEGER(),
                            sa.Computed('price * quantity', persisted=True))
                 )
