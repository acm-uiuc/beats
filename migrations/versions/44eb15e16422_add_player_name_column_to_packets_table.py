"""Add player_name column to packets table

Revision ID: 44eb15e16422
Revises: None
Create Date: 2014-09-16 13:47:22.130329

"""

# revision identifiers, used by Alembic.
revision = '44eb15e16422'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('packets', sa.Column('player_name', sa.String(length=16)))


def downgrade():
    op.drop_column('packets', 'player_name')
