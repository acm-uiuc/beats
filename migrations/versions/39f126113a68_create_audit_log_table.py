"""Create audit log table

Revision ID: 39f126113a68
Revises: bf0ac877b0c
Create Date: 2015-09-13 03:45:06.886460

"""

# revision identifiers, used by Alembic.
revision = '39f126113a68'
down_revision = 'bf0ac877b0c'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'audit_log',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('user', sa.String(8)),
        sa.Column('message', sa.String(200)),
        sa.Column('timestamp', sa.DateTime),
        sa.Column('player_name', sa.String(16))
    )


def downgrade():
    op.drop_table('audit_log')
