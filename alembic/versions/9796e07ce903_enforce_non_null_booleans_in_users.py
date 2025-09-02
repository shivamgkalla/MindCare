"""Enforce non-null booleans in Users

Revision ID: 9796e07ce903
Revises: 318b7b9ef05f
Create Date: 2025-08-18 15:15:59.378265

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9796e07ce903'
down_revision: Union[str, None] = '318b7b9ef05f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Fix existing NULLs first
    op.execute("UPDATE users SET is_verified = FALSE WHERE is_verified IS NULL;")
    op.execute("UPDATE users SET is_active = TRUE WHERE is_active IS NULL;")

    # Then alter the columns to be NOT NULL with defaults
    op.alter_column("users", "is_verified",
               existing_type=sa.Boolean(),
               nullable=False,
               server_default=sa.sql.expression.false())

    op.alter_column("users", "is_active",
               existing_type=sa.Boolean(),
               nullable=False,
               server_default=sa.sql.expression.true())


def downgrade() -> None:
    op.alter_column("users", "is_verified",
               existing_type=sa.Boolean(),
               nullable=True,
               server_default=None)

    op.alter_column("users", "is_active",
               existing_type=sa.Boolean(),
               nullable=True,
               server_default=None)
