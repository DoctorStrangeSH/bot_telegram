# scheduler.py
import asyncio
from datetime import datetime, timezone, timedelta

MOSCOW_TZ = timezone(timedelta(hours=3))

class Scheduler:
    def __init__(self, client, db, send_to_topic):
        self.client = client
        self.db = db
        self.send_to_topic = send_to_topic
        self.tasks = []
    
    def get_time(self):
        return datetime.now(MOSCOW_TZ)
    
    async def check_reminders(self):
        while True:
            try:
                reminders = self.db.get_pending_reminders()
                for reminder in reminders:
                    reminder_id, text, remind_at, is_done = reminder
                    await self.send_to_topic(3, f'⏰ **НАПОМИНАНИЕ!**\n\n{text}')
                    self.db.mark_reminder_done(reminder_id)
            except Exception as e:
                print(f"Ошибка: {e}")
            
            await asyncio.sleep(30)
    
    async def start(self):
        self.tasks.append(asyncio.create_task(self.check_reminders()))