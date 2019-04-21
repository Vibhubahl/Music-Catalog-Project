import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))


class MusicType(Base):
    __tablename__ = 'music_type'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'id': self.id,
        }


class MusicName(Base):
    __tablename__ = 'music_name'
    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    releaseyear = Column(String(100))
    artist = Column(String(100))
    musicname_id = Column(Integer, ForeignKey('music_type.id'))
    music_type = relationship(MusicType)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'id': self.id,
            'artist': self.artist,
            'releaseyear': self.releaseyear,
        }


engine = create_engine('sqlite:///musicitemcatalog.db')
Base.metadata.create_all(engine)
