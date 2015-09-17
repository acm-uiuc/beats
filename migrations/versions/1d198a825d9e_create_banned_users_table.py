"""Create banned users table

Revision ID: 1d198a825d9e
Revises: 39f126113a68
Create Date: 2015-09-17 00:37:37.682243

"""

# revision identifiers, used by Alembic.
revision = '1d198a825d9e'
down_revision = '39f126113a68'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'banned_users',
        sa.Column('username', sa.String(8), primary_key=True),
        sa.Column('reason', sa.String(200))
    )


def downgrade():
    op.drop_table('banned_users')
