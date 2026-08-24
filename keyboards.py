# keyboards.py
from telethon import Button

def get_main_keyboard():
    """Главное меню"""
    return [
        [Button.inline("✅ Онлайн", b"online"), Button.inline("🌙 Оффлайн", b"offline")],
        [Button.inline("📊 Статус", b"status"), Button.inline("🎭 Режим", b"mode")],
        [Button.inline("📈 Аналитика", b"analytics"), Button.inline("⚙️ Настройки", b"settings")],
    ]

def get_mode_keyboard():
    """Меню режимов"""
    return [
        [Button.inline("😊 Обычный", b"mode_normal"), Button.inline("😤 Занят", b"mode_busy")],
        [Button.inline("😴 Сплю", b"mode_sleeping"), Button.inline("🤝 Встреча", b"mode_meeting")],
    ]

def get_settings_keyboard():
    """Меню настроек"""
    return [
        [Button.inline("🔍 Фильтр", b"filter"), Button.inline("📋 Списки", b"lists")],
        [Button.inline("⏰ Расписание", b"schedule"), Button.inline("🔙 Назад", b"back")],
    ]

def get_filter_keyboard():
    """Меню фильтров"""
    return [
        [Button.inline("👥 Все", b"filter_all"), Button.inline("🤖 Только бот", b"filter_bot")],
        [Button.inline("⭐️ Белый список", b"filter_white"), Button.inline("🔙 Назад", b"back")],
    ]