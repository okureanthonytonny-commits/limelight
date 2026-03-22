"""add_stock_and_timestamps_to_product

Revision ID: 82555f47cd77
Revises: 77a120485a9d
Create Date: 2026-03-19 14:01:38.049193

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '82555f47cd77'
down_revision: Union[str, Sequence[str], None] = '77a120485a9d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add stock column to product table
    op.add_column('product', sa.Column('stock', sa.Integer(), nullable=False, server_default='0'))

    # Add role column to user table
    op.add_column('user', sa.Column('role', sa.String(length=50), nullable=False, server_default='customer'))

    # If any existing rows have NULL due to legacy schema, ensure default
    op.execute("UPDATE product SET stock = 0 WHERE stock IS NULL")
    op.execute("UPDATE \"user\" SET role = 'customer' WHERE role IS NULL")


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('user', 'role')
    op.drop_column('product', 'stock')
