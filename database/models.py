from sqlalchemy import Column, Integer, String, Date, Time, JSON
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    time = Column(Time, nullable=False)
    place = Column(String, nullable=False)
    address = Column(String, nullable=True)
    event_type = Column(String, nullable=False)
    guests = Column(JSON, nullable=True)  # список гостей
