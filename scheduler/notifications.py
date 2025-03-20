from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import timedelta
import datetime
from config import Config

scheduler = AsyncIOScheduler(timezone=Config.SCHEDULER_TIMEZONE)

def schedule_notification(user_id: int, event_time: datetime, event_name: str):
    # Уведомление за сутки
    notify_time_1_day = event_time - timedelta(days=1)
    scheduler.add_job(
        send_notification,
        "date",
        run_date=notify_time_1_day,
        args=(user_id, event_name, "1 день"),
    )

    # Уведомление за час
    notify_time_1_hour = event_time - timedelta(hours=1)
    scheduler.add_job(
        send_notification,
        "date",
        run_date=notify_time_1_hour,
        args=(user_id, event_name, "1 час"),
    )

    # Уведомление за пять минут
    notify_time_5_minutes = event_time - timedelta(minutes=5)
    scheduler.add_job(
        send_notification,
        "date",
        run_date=notify_time_5_minutes,
        args=(user_id, event_name, "5 минут"),
    )

async def send_notification(user_id: int, event_name: str, reminder_time: str):
    from main import bot
    await bot.send_message(user_id, f"Напоминание: событие '{event_name}' начнется через {reminder_time}!")