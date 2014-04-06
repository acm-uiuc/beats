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
        last = self.last_played()
        return {'id': self.id,
                'title': self.title,
                'artist': self.artist,
                'album': self.album,
                'length': self.length,
                'path': self.path,
                'tracknumber': self.tracknumber,
                'play_count': self.play_count(),
                'last_played': str(last) if last else None}

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
            return history_item.played

class PlayHistory(Base):
    __tablename__ = 'play_history'

    id = Column(Integer, primary_key=True)
    song_id = Column(Integer, ForeignKey('songs.id', ondelete='CASCADE'))
    played = Column(DateTime, default=datetime.datetime.utcnow)

class Packet(Base):
    __tablename__ = 'packets'

    id = Column(Integer, primary_key=True)
    song_id = Column(Integer, ForeignKey('songs.id', ondelete='CASCADE'), unique=True)
    url = Column(String(100), unique=True)
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

def init_db():
    Base.metadata.create_all(engine)

if __name__ == '__main__':
    init_db()
