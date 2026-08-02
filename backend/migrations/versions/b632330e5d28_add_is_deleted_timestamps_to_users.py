"""add is_deleted, timestamps to users

Revision ID: b632330e5d28
Revises: f58b4bf329f0
Create Date: 2026-08-02 20:37:40.256639

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b632330e5d28'
down_revision: Union[str, Sequence[str], None] = 'f58b4bf329f0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column(
        'users',
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true())
    )
    op.add_column(
        'users',
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default=sa.false())
    )
    op.add_column(
        'users',
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now())
    )
    op.add_column(
        'users',
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now())
    )


def downgrade():
    op.drop_column('users', 'updated_at')
    op.drop_column('users', 'created_at')
    op.drop_column('users', 'is_deleted')
    op.drop_column('users', 'is_active')
