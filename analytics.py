# analytics.py
from datetime import datetime, timezone, timedelta

MOSCOW_TZ = timezone(timedelta(hours=3))

class Analytics:
    def __init__(self, db):
        self.db = db
    
    def get_daily_stats(self):
        """Статистика за сегодня"""
        now = datetime.now(MOSCOW_TZ)
        today_start = now.replace(hour=0, minute=0, second=0).isoformat()
        
        self.db.cursor.execute('''
            SELECT COUNT(*) FROM messages WHERE timestamp >= ?
        ''', (today_start,))
        messages_today = self.db.cursor.fetchone()[0]
        
        self.db.cursor.execute('''
            SELECT COUNT(DISTINCT user_id) FROM users WHERE last_seen >= ?
        ''', (today_start,))
        users_today = self.db.cursor.fetchone()[0]
        
        return {
            "messages_today": messages_today,
            "users_today": users_today,
        }
    
    def get_weekly_stats(self):
        """Статистика за неделю"""
        now = datetime.now(MOSCOW_TZ)
        week_start = (now - timedelta(days=7)).isoformat()
        
        self.db.cursor.execute('''
            SELECT COUNT(*) FROM messages WHERE timestamp >= ?
        ''', (week_start,))
        messages_week = self.db.cursor.fetchone()[0]
        
        return {
            "messages_week": messages_week,
        }
    
    def get_activity_by_hour(self):
        """Активность по часам"""
        self.db.cursor.execute('''
            SELECT substr(timestamp, 12, 2) as hour, COUNT(*)
            FROM messages
            GROUP BY hour
            ORDER BY hour
        ''')
        return self.db.cursor.fetchall()
    
    def generate_report(self):
        """Генерация полного отчёта"""
        daily = self.get_daily_stats()
        weekly = self.get_weekly_stats()
        top_users = self.db.get_top_users(5)
        
        report = f"""📊 **ОТЧЁТ**

📅 Сегодня:
• Сообщений: {daily['messages_today']}
• Пользователей: {daily['users_today']}

📆 За неделю:
• Сообщений: {weekly['messages_week']}

🏆 Топ собеседников:
"""
        for user_id, name, count in top_users:
            report += f"• {name}: {count} сообщ.\n"
        
        return report

analytics = Analytics(db)