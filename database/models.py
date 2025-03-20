from sqlalchemy import Column, Integer, String, DateTime
from database.connection import Base

class Event(Base):
    __tablename__ = 'events'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    date = Column(String)
    time = Column(String)
    place = Column(String)
    address = Column(String)
    event_type = Column(String)
    guests = Column(String)