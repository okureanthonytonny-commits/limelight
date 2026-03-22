"""empty message

Revision ID: 9d2306189058
Revises: a0b8d660cd54, a1c2d3e4f5g6
Create Date: 2026-03-21 18:24:33.204046

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9d2306189058'
down_revision: Union[str, Sequence[str], None] = ('a0b8d660cd54', 'a1c2d3e4f5g6')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
