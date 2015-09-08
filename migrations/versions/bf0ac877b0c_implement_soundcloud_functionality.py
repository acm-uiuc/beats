"""Implement Soundcloud functionality

Revision ID: bf0ac877b0c
Revises: 26d705ab8fbc
Create Date: 2015-09-07 23:55:56.201101

"""

# revision identifiers, used by Alembic.
revision = 'bf0ac877b0c'
down_revision = '26d705ab8fbc'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('packets', sa.Column('soundcloud_url', sa.String(length=100)))
    op.add_column('packets', sa.Column('soundcloud_id', sa.String(length=32)))
    op.add_column('packets', sa.Column('art_uri', sa.String(length=32)))
    op.add_column('packets', sa.Column('artist', sa.Unicode(length=100)))
    # change column sizes
    op.alter_column('songs', 'title', type_=sa.Unicode(length=200), existing_type=sa.Unicode(length=100))
    op.alter_column('songs', 'artist', type_=sa.Unicode(length=200), existing_type=sa.Unicode(length=100))
    op.alter_column('songs', 'album', type_=sa.Unicode(length=200), existing_type=sa.Unicode(length=100))


def downgrade():
    op.drop_column('packets', 'soundcloud_url')
    op.drop_column('packets', 'soundcloud_id')
    op.drop_column('packets', 'art_uri')
    op.drop_column('packets', 'artist')
    # revert column sizes
    op.alter_column('songs', 'title', type_=sa.Unicode(length=100), existing_type=sa.Unicode(length(length=200)))
    op.alter_column('songs', 'artist', type_=sa.Unicode(length=100), existing_type=sa.Unicode(length(length=200)))
    op.alter_column('songs', 'album', type_=sa.Unicode(length=100), existing_type=sa.Unicode(length(length=200)))
