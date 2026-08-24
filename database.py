# database.py
import sqlite3
import json
from datetime import datetime, timezone, timedelta

MOSCOW_TZ = timezone(timedelta(hours=3))

class Database:
    def __init__(self, db_name="bot.db"):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.create_tables()
    
    def create_tables(self):
        """Создание таблиц"""
        # Пользователи
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                name TEXT,
                username TEXT,
                is_white BOOLEAN DEFAULT 0,
                is_black BOOLEAN DEFAULT 0,
                first_seen TEXT,
                last_seen TEXT,
                message_count INTEGER DEFAULT 0
            )
        ''')
        
        # Сообщения
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                text TEXT,
                timestamp TEXT,
                is_reply BOOLEAN DEFAULT 0
            )
        ''')
        
        # Настройки
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')
        
        # Расписание
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS schedule (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                time TEXT,
                action TEXT,
                enabled BOOLEAN DEFAULT 1
            )
        ''')
        
        # Напоминания
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT,
                remind_at TEXT,
                is_done BOOLEAN DEFAULT 0
            )
        ''')
        
        self.conn.commit()
    
    # === ПОЛЬЗОВАТЕЛИ ===
    def add_user(self, user_id, name, username=None):
        now = datetime.now(MOSCOW_TZ).isoformat()
        self.cursor.execute('''
            INSERT OR IGNORE INTO users (user_id, name, username, first_seen, last_seen)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, name, username, now, now))
        self.cursor.execute('''
            UPDATE users SET last_seen = ?, message_count = message_count + 1
            WHERE user_id = ?
        ''', (now, user_id))
        self.conn.commit()
    
    def get_user(self, user_id):
        self.cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        return self.cursor.fetchone()
    
    def set_white(self, user_id, status=True):
        self.cursor.execute('UPDATE users SET is_white = ? WHERE user_id = ?', (status, user_id))
        self.conn.commit()
    
    def set_black(self, user_id, status=True):
        self.cursor.execute('UPDATE users SET is_black = ? WHERE user_id = ?', (status, user_id))
        self.conn.commit()
    
    def get_white_list(self):
        self.cursor.execute('SELECT user_id FROM users WHERE is_white = 1')
        return [row[0] for row in self.cursor.fetchall()]
    
    def get_black_list(self):
        self.cursor.execute('SELECT user_id FROM users WHERE is_black = 1')
        return [row[0] for row in self.cursor.fetchall()]
    
    # === СООБЩЕНИЯ ===
    def add_message(self, user_id, text):
        now = datetime.now(MOSCOW_TZ).isoformat()
        self.cursor.execute('''
            INSERT INTO messages (user_id, text, timestamp)
            VALUES (?, ?, ?)
        ''', (user_id, text, now))
        self.conn.commit()
    
    def get_messages(self, user_id=None, limit=50):
        if user_id:
            self.cursor.execute('SELECT * FROM messages WHERE user_id = ? ORDER BY id DESC LIMIT ?', (user_id, limit))
        else:
            self.cursor.execute('SELECT * FROM messages ORDER BY id DESC LIMIT ?', (limit,))
        return self.cursor.fetchall()
    
    # === СТАТИСТИКА ===
    def get_top_users(self, limit=10):
        self.cursor.execute('''
            SELECT user_id, name, message_count FROM users
            ORDER BY message_count DESC LIMIT ?
        ''', (limit,))
        return self.cursor.fetchall()
    
    def get_total_messages(self):
        self.cursor.execute('SELECT COUNT(*) FROM messages')
        return self.cursor.fetchone()[0]
    
    # === НАСТРОЙКИ ===
    def set_setting(self, key, value):
        self.cursor.execute('''
            INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)
        ''', (key, json.dumps(value)))
        self.conn.commit()
    
    def get_setting(self, key, default=None):
        self.cursor.execute('SELECT value FROM settings WHERE key = ?', (key,))
        row = self.cursor.fetchone()
        if row:
            return json.loads(row[0])
        return default
    
    # === РАСПИСАНИЕ ===
    def add_schedule(self, time_str, action):
        self.cursor.execute('''
            INSERT INTO schedule (time, action) VALUES (?, ?)
        ''', (time_str, action))
        self.conn.commit()
    
    def get_schedule(self):
        self.cursor.execute('SELECT * FROM schedule WHERE enabled = 1')
        return self.cursor.fetchall()
    
    # === НАПОМИНАНИЯ ===
    def add_reminder(self, text, remind_at):
        self.cursor.execute('''
            INSERT INTO reminders (text, remind_at) VALUES (?, ?)
        ''', (text, remind_at))
        self.conn.commit()
    
    def get_pending_reminders(self):
        now = datetime.now(MOSCOW_TZ).isoformat()
        self.cursor.execute('''
            SELECT * FROM reminders WHERE is_done = 0 AND remind_at <= ?
        ''', (now,))
        return self.cursor.fetchall()
    
    def mark_reminder_done(self, reminder_id):
        self.cursor.execute('UPDATE reminders SET is_done = 1 WHERE id = ?', (reminder_id,))
        self.conn.commit()
    
    def close(self):
        self.conn.close()

db = Database()