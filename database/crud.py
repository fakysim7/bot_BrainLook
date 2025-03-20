from sqlalchemy.orm import Session
from database.models import Event

async def create_event(title, date, time, place, address, event_type, guests):
    db = Session()
    event = Event(
        title=title,
        date=date,
        time=time,
        place=place,
        address=address,
        event_type=event_type,
        guests=guests
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    db.close()