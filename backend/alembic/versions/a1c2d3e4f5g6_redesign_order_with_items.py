"""redesign_order_with_items

Revision ID: a1c2d3e4f5g6
Revises: 82555f47cd77
Create Date: 2026-03-20 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'a1c2d3e4f5g6'
down_revision: Union[str, Sequence[str], None] = '82555f47cd77'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema: redesign order table and create orderitem table."""
    # Drop old order table if it exists
    #op.drop_table('order')

    # Create new order table with proper schema
    op.create_table(
        'order',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('status', sqlmodel.sql.sqltypes.AutoString(length=20), nullable=False, server_default='pending'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_order_user_id'), 'order', ['user_id'], unique=False)

    # Create orderitem table
    op.create_table(
        'orderitem',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('order_id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('price', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.ForeignKeyConstraint(['order_id'], ['order.id'], ),
        sa.ForeignKeyConstraint(['product_id'], ['product.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_orderitem_order_id'), 'orderitem', ['order_id'], unique=False)
    op.create_index(op.f('ix_orderitem_product_id'), 'orderitem', ['product_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema: drop orderitem and revert order table."""
    op.drop_index(op.f('ix_orderitem_product_id'), table_name='orderitem')
    op.drop_index(op.f('ix_orderitem_order_id'), table_name='orderitem')
    op.drop_table('orderitem')

    op.drop_index(op.f('ix_order_user_id'), table_name='order')
    op.drop_table('order')

    # Restore old simple order table (if needed)
    op.create_table(
        'order',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('total_price', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
