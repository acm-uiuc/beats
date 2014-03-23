from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, ForeignKey, UniqueConstraint
from sqlalchemy.orm import sessionmaker, relationship

engine = create_engine('sqlite:///acoustics.db', echo=True)
Session = sessionmaker(bind=engine)
Base = declarative_base()

class Song(Base):
    __tablename__ = 'songs'

    id = Column(Integer, primary_key=True)
    title = Column(String)
    artist = Column(String)
    album = Column(String)
    length = Column(Float)
    path = Column(String)
    tracknumber = Column(Integer)
    packet = relationship('Packet', uselist=False, cascade='all,delete-orphan', passive_deletes=True, backref='songs')

    def mrl(self):
        return 'file://' + self.path

    def dictify(self):
        return {'title': self.title,
                'album': self.album,
                'length': self.length,
                'path': self.path,
                'tracknumber': self.tracknumber}

class Packet(Base):
    __tablename__ = 'packets'

    song_id = Column(Integer, ForeignKey('songs.id', ondelete='CASCADE'), primary_key=True)
    user = Column(String)
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
    user = Column(String)

    __table_args__ = (UniqueConstraint('packet_id', 'user'),
            )

def init_db():
    Base.metadata.create_all(engine)

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

if __name__ == '__main__':
    init_db()
