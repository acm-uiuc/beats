"""Implement SoundCloud functionality

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
    op.add_column('packets', sa.Column('stream_id', sa.String(length=32)))
    op.add_column('packets', sa.Column('art_uri', sa.String(length=100)))
    op.add_column('packets', sa.Column('artist', sa.Unicode(length=100)))
    # change column sizes
    op.alter_column('songs', 'title', type_=sa.Unicode(length=200), existing_type=sa.Unicode(length=100))
    op.alter_column('songs', 'artist', type_=sa.Unicode(length=200), existing_type=sa.Unicode(length=100))
    op.alter_column('songs', 'album', type_=sa.Unicode(length=200), existing_type=sa.Unicode(length=100))
    # rename columns
    op.alter_column('packets', 'video_url', new_column_name='stream_url', existing_type=sa.String(length=100))
    op.alter_column('packets', 'video_title', new_column_name='stream_title', existing_type=sa.Unicode(length=100))
    op.alter_column('packets', 'video_length', new_column_name='stream_length', existing_type=sa.Float)


def downgrade():
    op.drop_column('packets', 'stream_id')
    op.drop_column('packets', 'art_uri')
    op.drop_column('packets', 'artist')
    # revert column sizes
    op.alter_column('songs', 'title', type_=sa.Unicode(length=100), existing_type=sa.Unicode(length=200))
    op.alter_column('songs', 'artist', type_=sa.Unicode(length=100), existing_type=sa.Unicode(length=200))
    op.alter_column('songs', 'album', type_=sa.Unicode(length=100), existing_type=sa.Unicode(length=200))
    # revert renames
    op.alter_column('packets', 'stream_url', new_column_name='video_url', existing_type=sa.String(length=100))
    op.alter_column('packets', 'stream_title', new_column_name='video_title', existing_type=sa.Unicode(length=100))
    op.alter_column('packets', 'stream_length', new_column_name='video_length', existing_type=sa.Float)
