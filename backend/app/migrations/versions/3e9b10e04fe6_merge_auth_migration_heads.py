"""merge auth migration heads

Revision ID: 3e9b10e04fe6
Revises: 4f9c98227fbb, f33e1b168d51
Create Date: 2025-12-25 12:55:22.621736

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3e9b10e04fe6'
down_revision: Union[str, Sequence[str], None] = ('4f9c98227fbb', 'f33e1b168d51')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
