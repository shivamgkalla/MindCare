"""Add profile fields to users and create coach_profiles table

Revision ID: 318b7b9ef05f
Revises: a98ba8773467
Create Date: 2025-08-14 13:42:30.145790

"""
from typing import Sequence, Union
import enum

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '318b7b9ef05f'
down_revision: Union[str, None] = 'a98ba8773467'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


class GenderEnum(str, enum.Enum):
    male = "male"
    female = "female"
    other = "other"


def upgrade():
    gender_enum = sa.Enum(GenderEnum, name="genderenum")
    gender_enum.create(op.get_bind(), checkfirst=True)
    # Add new profile fields to 'users' table
    op.add_column('users', sa.Column('age', sa.Integer(), nullable=True))
    op.add_column('users', sa.Column('gender', sa.Enum(GenderEnum), nullable=True))
    op.add_column('users', sa.Column('location', sa.String(), nullable=True))
    op.add_column('users', sa.Column('profile_photo', sa.String(), nullable=True))

    # Create 'coach_profiles' table
    op.create_table(
        'coach_profiles',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), unique=True, nullable=False),
        sa.Column('qualifications', sa.String(), nullable=False),
        sa.Column('specialization', sa.String(), nullable=False),
        sa.Column('experience_years', sa.Integer(), nullable=False),
        sa.Column('charges_per_slot', sa.Numeric(10, 2), nullable=True),
        sa.Column('availability_status', sa.Boolean(), server_default=sa.text("true"))
    )

def downgrade():
    op.drop_table('coach_profiles')
    op.drop_column('users', 'profile_photo')
    op.drop_column('users', 'location')
    op.drop_column('users', 'gender')
    op.drop_column('users', 'age')

    gender_enum = sa.Enum(GenderEnum, name="genderenum")
    gender_enum.drop(op.get_bind(), checkfirst=True)