"""Add image_url column to journals table

Revision ID: 067c86e2920d
Revises: 18d60e667854
Create Date: 2025-08-26 12:14:31.383717

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '067c86e2920d'
down_revision: Union[str, None] = '18d60e667854'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "journals",
        sa.Column("image_url", sa.String(length=500), nullable=True)
    )



def downgrade() -> None:
    op.drop_column("journals", "image_url")
