from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, ForeignKey, UniqueConstraint
from sqlalchemy.orm import sessionmaker, relationship
from config import config

DATABASE_URL = config.get('Database', 'url')

engine = create_engine(DATABASE_URL, pool_recycle=3600)
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

    def mrl(self):
        return 'file://' + self.path

    def dictify(self):
        return {'id': self.id,
                'title': self.title,
                'album': self.album,
                'length': self.length,
                'path': self.path,
                'tracknumber': self.tracknumber}

class Packet(Base):
    __tablename__ = 'packets'

    song_id = Column(Integer, ForeignKey('songs.id', ondelete='CASCADE'), primary_key=True)
    user = Column(String(8))
    arrival_time = Column(Float)
    finish_time = Column(Float)
    additional_votes = relationship('Vote', cascade='all,delete-orphan', passive_deletes=True, backref='packets')

    def num_votes(self):
        return 1 + len(self.additional_votes)

    def weight(self):
        # The 1 denotes the user weight
        return 1 * 2 ** (self.num_votes() - 1)

class Vote(Base):
    __tablename__ = 'votes'

    id = Column(Integer, primary_key=True)
    packet_id = Column(Integer, ForeignKey('packets.song_id', ondelete='CASCADE'))
    user = Column(String(8))

    __table_args__ = (UniqueConstraint('packet_id', 'user'),
            )

def init_db():
    Base.metadata.create_all(engine)

if __name__ == '__main__':
    init_db()
