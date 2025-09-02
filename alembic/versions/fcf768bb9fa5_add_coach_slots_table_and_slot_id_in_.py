"""Add coach_slots table and slot_id in bookings table

Revision ID: fcf768bb9fa5
Revises: 067c86e2920d
Create Date: 2025-08-26 15:30:21.162470
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'fcf768bb9fa5'
down_revision: Union[str, None] = '067c86e2920d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create coach_slots table
    op.create_table(
        'coach_slots',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('coach_id', sa.Integer(), nullable=False),
        sa.Column('start_time', sa.DateTime(), nullable=False),
        sa.Column('end_time', sa.DateTime(), nullable=False),
        sa.Column('price', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('is_booked', sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(['coach_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_coach_slots_id'), 'coach_slots', ['id'], unique=False)

    # Add slot_id column to bookings table
    op.add_column('bookings', sa.Column('slot_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'bookings', 'coach_slots', ['slot_id'], ['id'], ondelete='SET NULL')

    # Add unique constraint for slot_id
    op.create_unique_constraint('uq_booking_slot', 'bookings', ['slot_id'])


def downgrade() -> None:
    # Drop unique constraint first
    op.drop_constraint('uq_booking_slot', 'bookings', type_='unique')
    
    # Drop foreign key and column
    op.drop_constraint(None, 'bookings', type_='foreignkey')
    op.drop_column('bookings', 'slot_id')

    # Drop coach_slots table
    op.drop_index(op.f('ix_coach_slots_id'), table_name='coach_slots')
    op.drop_table('coach_slots')
