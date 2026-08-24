# security.py
from datetime import datetime, timezone, timedelta
import hashlib

MOSCOW_TZ = timezone(timedelta(hours=3))

class Security:
    def __init__(self, db):
        self.db = db
        self.rate_limits = {}  # user_id: [timestamps]
        self.max_messages_per_minute = 10
        self.banned_users = set()
    
    def check_rate_limit(self, user_id):
        """Проверка лимита сообщений"""
        now = datetime.now(MOSCOW_TZ)
        minute_ago = now - timedelta(minutes=1)
        
        if user_id not in self.rate_limits:
            self.rate_limits[user_id] = []
        
        # Очищаем старые
        self.rate_limits[user_id] = [
            ts for ts in self.rate_limits[user_id]
            if ts > minute_ago
        ]
        
        if len(self.rate_limits[user_id]) >= self.max_messages_per_minute:
            return False
        
        self.rate_limits[user_id].append(now)
        return True
    
    def is_banned(self, user_id):
        """Проверка бана"""
        return user_id in self.banned_users
    
    def ban_user(self, user_id):
        """Забанить пользователя"""
        self.banned_users.add(user_id)
    
    def unban_user(self, user_id):
        """Разбанить пользователя"""
        self.banned_users.discard(user_id)
    
    def hash_password(self, password):
        """Хеширование пароля"""
        return hashlib.sha256(password.encode()).hexdigest()

security = Security(db)