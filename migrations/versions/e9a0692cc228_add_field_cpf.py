"""add field cpf

Revision ID: e9a0692cc228
Revises: 262cf9b56e1c
Create Date: 2024-08-20 19:52:56.767667

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e9a0692cc228'
down_revision: Union[str, None] = '262cf9b56e1c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('cpf', sa.String(), nullable=False))
    op.create_unique_constraint(None, 'users', ['cpf'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'users', type_='unique')
    op.drop_column('users', 'cpf')
    # ### end Alembic commands ###
