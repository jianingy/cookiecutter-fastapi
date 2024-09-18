"""initial commit

Revision ID: eacb1a847242
Revises:
Create Date: 2024-09-15 20:44:22.588809+08:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'eacb1a847242'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('admin_users',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('username', sa.String(length=20), nullable=False),
                    sa.Column('password', sa.String(), nullable=False),
                    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
                    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('username')
                    )
    op.create_index(op.f('ix_admin_users_created_at'), 'admin_users', ['created_at'], unique=False)
    op.create_index(op.f('ix_admin_users_updated_at'), 'admin_users', ['updated_at'], unique=False)


def downgrade() -> None:
    op.drop_table('admin_users')
