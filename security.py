# security.py
from datetime import datetime, timezone, timedelta
import hashlib
from database import db  # ← Добавь этот импорт!

MOSCOW_TZ = timezone(timedelta(hours=3))

class Security:
    def __init__(self, database):
        self.db = database
        self.rate_limits = {}
        self.max_messages_per_minute = 10
        self.banned_users = set()
    
    def check_rate_limit(self, user_id):
        now = datetime.now(MOSCOW_TZ)
        minute_ago = now - timedelta(minutes=1)
        
        if user_id not in self.rate_limits:
            self.rate_limits[user_id] = []
        
        self.rate_limits[user_id] = [
            ts for ts in self.rate_limits[user_id]
            if ts > minute_ago
        ]
        
        if len(self.rate_limits[user_id]) >= self.max_messages_per_minute:
            return False
        
        self.rate_limits[user_id].append(now)
        return True
    
    def is_banned(self, user_id):
        return user_id in self.banned_users
    
    def ban_user(self, user_id):
        self.banned_users.add(user_id)
    
    def unban_user(self, user_id):
        self.banned_users.discard(user_id)

security = Security(db)