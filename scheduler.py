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
        """Проверяет и отправляет напоминания"""
        while True:
            try:
                reminders = self.db.get_pending_reminders()
                for reminder in reminders:
                    reminder_id, text, remind_at, is_done = reminder
                    await self.send_to_topic(3, f'⏰ **НАПОМИНАНИЕ!**\n\n{text}')
                    self.db.mark_reminder_done(reminder_id)
            except Exception as e:
                print(f"Ошибка проверки напоминаний: {e}")
            
            await asyncio.sleep(30)
    
    async def check_schedule(self):
        """Проверяет расписание"""
        while True:
            try:
                now = self.get_time()
                current_time = now.strftime("%H:%M")
                
                schedule = self.db.get_schedule()
                for item in schedule:
                    sched_id, time_str, action, enabled = item
                    if time_str == current_time:
                        if action == "morning_report":
                            await self.send_morning_report()
                        elif action == "evening_report":
                            await self.send_evening_report()
                        elif action == "auto_offline":
                            await self.send_to_topic(4, "🌙 Автоматическое включение оффлайн режима")
            except Exception as e:
                print(f"Ошибка расписания: {e}")
            
            await asyncio.sleep(60)
    
    async def send_morning_report(self):
        """Утренний отчёт"""
        now = self.get_time()
        total_users = len(self.db.get_top_users(100))
        total_messages = self.db.get_total_messages()
        
        report = f"""☀️ **Утренний отчёт**

📅 Дата: {now.strftime('%d.%m.%Y')}
🕐 Время: {now.strftime('%H:%M')}

📊 Всего пользователей: {total_users}
💬 Всего сообщений: {total_messages}"""
        
        await self.send_to_topic(4, report)
    
    async def send_evening_report(self):
        """Вечерний отчёт"""
        now = self.get_time()
        top_users = self.db.get_top_users(5)
        
        report = f"🌙 **Вечерний отчёт**\n\n📅 {now.strftime('%d.%m.%Y')}\n\nТоп собеседников:\n"
        for user_id, name, count in top_users:
            report += f"• {name}: {count} сообщ.\n"
        
        await self.send_to_topic(4, report)
    
    async def start(self):
        """Запуск всех задач"""
        self.tasks.append(asyncio.create_task(self.check_reminders()))
        self.tasks.append(asyncio.create_task(self.check_schedule()))