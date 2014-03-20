from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, ForeignKey
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
    packet = relationship('Packet', uselist=False, backref='songs')

    def mrl(self):
        return 'file://' + self.path

class Packet(Base):
    __tablename__ = 'packets'

    song_id = Column(Integer, ForeignKey('songs.id'), primary_key=True)
    user = Column(String)
    arrival_time = Column(Float)
