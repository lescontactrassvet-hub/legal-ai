"""add is_superuser to users

Revision ID: f33e1b168d51
Revises: c8627650149b
Create Date: 2025-12-25 04:21:47.523312

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f33e1b168d51'
down_revision: Union[str, Sequence[str], None] = 'c8627650149b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("users", sa.Column("is_superuser", sa.Boolean(), server_default=sa.false(), nullable=False))



def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("users", "is_superuser")

