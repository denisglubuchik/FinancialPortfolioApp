"""users model changed

Revision ID: 79b171bbac79
Revises: c341d34bbe0f
Create Date: 2024-10-28 15:47:10.662831

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '79b171bbac79'
down_revision: Union[str, None] = 'c341d34bbe0f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'external_user_id')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('external_user_id', sa.INTEGER(), autoincrement=False, nullable=False))
    # ### end Alembic commands ###
