"""Remove unique constraint on video_url from packets

Revision ID: 26d705ab8fbc
Revises: 44eb15e16422
Create Date: 2014-09-19 23:25:02.862445

"""

# revision identifiers, used by Alembic.
revision = '26d705ab8fbc'
down_revision = '44eb15e16422'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.drop_constraint('video_url', 'packets', type_='unique')
    pass


def downgrade():
    op.create_unique_constraint('video_url', 'packets', ['video_url'])
    pass
