from sqlalchemy import Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    jobs = relationship('AudioJob', back_populates='user')

class AudioJob(Base):
    __tablename__ = 'audio_jobs'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    language = Column(String)
    filename = Column(String)
    user = relationship('User', back_populates='jobs')
    segments = relationship('Segment', back_populates='job')

class Segment(Base):
    __tablename__ = 'segments'
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey('audio_jobs.id'))
    start = Column(Float)
    end = Column(Float)
    transcript = Column(String, default='')
    job = relationship('AudioJob', back_populates='segments')
