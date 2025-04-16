from sqlalchemy.ext.asyncio import AsyncSession
from database.models import Event

async def create_event(session: AsyncSession, title, date, time, place, address, event_type, guests):
    new_event = Event(
        title=title,
        date=date,
        time=time,
        place=place,
        address=address,
        event_type=event_type,
        guests=guests
    )
    session.add(new_event)
    await session.commit()
    await session.refresh(new_event)
    return new_event
