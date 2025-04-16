from sqlalchemy.orm import Session
from database.models import Event
from database.connection import get_sync_session  # импортируем функцию создания сессии

def create_event(title, date, time, place, address, event_type, guests):
    with get_sync_session() as db:  # Контекстный менеджер, автоматически закроет сессию
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
        return event
