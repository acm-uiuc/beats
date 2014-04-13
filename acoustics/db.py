from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.pool import NullPool
from config import config
import datetime

DATABASE_URL = config.get('Database', 'url')

engine = create_engine(DATABASE_URL, poolclass=NullPool)
Session = sessionmaker(bind=engine)
Base = declarative_base()

class Song(Base):
    __tablename__ = 'songs'

    id = Column(Integer, primary_key=True)
    title = Column(String(100))
    artist = Column(String(100))
    album = Column(String(100))
    length = Column(Float)
    path = Column(String(500))
    tracknumber = Column(Integer)
    packet = relationship('Packet', uselist=False, cascade='all,delete-orphan', passive_deletes=True, backref='songs')
    history = relationship('PlayHistory', cascade='all,delete-orphan', passive_deletes=True, backref='songs')

    def mrl(self):
        return 'file://' + self.path

    def dictify(self):
        return {'id': self.id,
                'title': self.title,
                'artist': self.artist,
                'album': self.album,
                'length': self.length,
                'path': self.path,
                'tracknumber': self.tracknumber}

    def play_count(self):
        session = Session()
        count = session.query(PlayHistory).filter_by(song_id=self.id).count()
        session.commit()
        return count

    def last_played(self):
        session = Session()
        history_item = session.query(PlayHistory).filter_by(song_id=self.id).order_by(PlayHistory.id.desc()).first()
        session.commit()
        if history_item:
            return history_item.played_at

class PlayHistory(Base):
    __tablename__ = 'play_history'

    id = Column(Integer, primary_key=True)
    song_id = Column(Integer, ForeignKey('songs.id', ondelete='CASCADE'))
    user = Column(String(8))
    played_at = Column(DateTime, default=datetime.datetime.utcnow)

class Packet(Base):
    __tablename__ = 'packets'

    id = Column(Integer, primary_key=True)
    song_id = Column(Integer, ForeignKey('songs.id', ondelete='CASCADE'), unique=True)
    video_url = Column(String(100), unique=True)
    video_title = Column(String(100))
    video_length = Column(Float)
    user = Column(String(8))
    arrival_time = Column(Float)
    finish_time = Column(Float)
    additional_votes = relationship('Vote', cascade='all,delete-orphan', passive_deletes=True, backref='packets')

    def num_votes(self):
        return 1 + len(self.additional_votes)

    def weight(self):
        # The 1 denotes the user weight
        return 1 * 2 ** (self.num_votes() - 1)

    def has_voted(self, user):
        return self.user == user or any(vote.user == user for vote in self.additional_votes)

class Vote(Base):
    __tablename__ = 'votes'

    packet_id = Column(Integer, ForeignKey('packets.id', ondelete='CASCADE'), primary_key=True)
    user = Column(String(8), primary_key=True)

class Playlist(Base):
    __tablename__ = 'playlists'

    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    user = Column(String(8))

class PlaylistItem(Base):
    __tablename__ = 'playlist_items'

    playlist_id = Column(Integer, ForeignKey('playlists.id', ondelete='CASCADE'), primary_key=True)
    index = Column(Integer, primary_key=True, autoincrement=False)
    song_id = Column(Integer, ForeignKey('songs.id', ondelete='CASCADE'))

    __table_args__ = (UniqueConstraint('playlist_id', 'song_id'),
            )

def init_db():
    Base.metadata.create_all(engine)

if __name__ == '__main__':
    init_db()
