# filters.py
from datetime import datetime, timezone, timedelta
import re

MOSCOW_TZ = timezone(timedelta(hours=3))

class SmartFilter:
    def __init__(self):
        self.spam_words = ["спам", "реклама", "купить", "продам", "заработок", "casino"]
        self.important_words = ["срочно", "важно", "деньги", "оплата", "договор"]
        self.max_messages_per_minute = 5
        self.user_messages = {}  # user_id: [(timestamp, text), ...]
    
    def is_spam(self, text):
        """Проверка на спам"""
        if not text:
            return False
        text_lower = text.lower()
        return any(word in text_lower for word in self.spam_words)
    
    def is_important(self, text):
        """Проверка на важность"""
        if not text:
            return False
        text_lower = text.lower()
        return any(word in text_lower for word in self.important_words)
    
    def check_flood(self, user_id):
        """Проверка на флуд"""
        now = datetime.now(MOSCOW_TZ)
        minute_ago = now - timedelta(minutes=1)
        
        if user_id not in self.user_messages:
            self.user_messages[user_id] = []
        
        # Очищаем старые
        self.user_messages[user_id] = [
            (ts, text) for ts, text in self.user_messages[user_id]
            if ts > minute_ago
        ]
        
        return len(self.user_messages[user_id]) >= self.max_messages_per_minute
    
    def add_message(self, user_id, text):
        """Добавляет сообщение в историю"""
        now = datetime.now(MOSCOW_TZ)
        if user_id not in self.user_messages:
            self.user_messages[user_id] = []
        self.user_messages[user_id].append((now, text))
    
    def get_message_category(self, user_id, text):
        """Определяет категорию сообщения"""
        if self.is_spam(text):
            return "spam"
        if self.is_important(text):
            return "important"
        if self.check_flood(user_id):
            return "flood"
        return "normal"

smart_filter = SmartFilter()