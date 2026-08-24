# secretary.py
import asyncio
import logging
from datetime import datetime, timezone, timedelta
from telethon import TelegramClient, events
from telethon.sessions import StringSession

from config import *
from database import db
from filters import smart_filter
from analytics import analytics
from security import security

# Логирование
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

# Состояние
is_online = False
current_mode = "normal"
FILTER_MODE = "all"

def get_time():
    return datetime.now(MOSCOW_TZ)

def get_auto_reply(name):
    hour = get_time().hour
    
    mode_replies = {
        "normal": {
            "morning": f"☀️ Доброе утро, {name}! Sherlock скоро ответит.",
            "day": f"👨‍💻 Добрый день, {name}! Sherlock на связи.",
            "evening": f"🌆 Добрый вечер, {name}! Sherlock отошёл.",
            "night": f"🌙 Ночь! Sherlock спит. Не будить!",
        },
        "busy": {
            "morning": f"😤 {name}, Sherlock очень занят!",
            "day": f"😤 {name}, Sherlock на важном деле!",
            "evening": f"😤 {name}, Sherlock работает!",
            "night": f"😤 {name}, даже ночью занят!",
        },
        "sleeping": {
            "morning": f"😴 {name}, Sherlock ещё спит...",
            "day": f"😴 {name}, Sherlock спит.",
            "evening": f"😴 {name}, Sherlock уснул.",
            "night": f"😴 {name}, Sherlock крепко спит!",
        },
        "meeting": {
            "morning": f"🤝 {name}, Sherlock на встрече.",
            "day": f"🤝 {name}, Sherlock на встрече.",
            "evening": f"🤝 {name}, встреча затянулась...",
            "night": f"🤝 {name}, встреча...",
        },
    }
    
    if 5 <= hour < 12:
        time_key = "morning"
    elif 12 <= hour < 17:
        time_key = "day"
    elif 17 <= hour < 23:
        time_key = "evening"
    else:
        time_key = "night"
    
    return mode_replies[current_mode][time_key]

async def send_to_topic(topic_id, message):
    try:
        await client.send_message(GROUP_ID, message, reply_to=topic_id)
        logger.info(f"Отправлено в тему {topic_id}")
    except Exception as e:
        logger.error(f"Ошибка отправки: {e}")

# === КОМАНДЫ (без кнопок) ===

@client.on(events.NewMessage(pattern=r'\.menu'))
async def show_menu(event):
    menu_text = """🎛 **МЕНЮ**

**Статусы:**
.online — включить онлайн
.offline — включить оффлайн
.status — проверить статус

**Режимы:**
.mode normal — обычный
.mode busy — занят
.mode sleeping — сплю
.mode meeting — встреча

**Инструменты:**
.stats — статистика
.analytics — аналитика
.remind — напоминание

**Списки:**
.addwhite — белый список
.addblack — чёрный список

**Настройки:**
.filter — фильтрация
.help — все команды"""
    
    await event.reply(menu_text)

@client.on(events.NewMessage(pattern=r'\.mode'))
async def set_mode(event):
    global current_mode
    
    text = event.text.replace('.mode', '').strip().lower()
    modes = {
        "normal": "😊 Обычный",
        "busy": "😤 Занят",
        "sleeping": "😴 Сплю",
        "meeting": "🤝 Встреча",
    }
    
    if text in modes:
        current_mode = text
        await event.reply(f'✅ Режим: {modes[text]}')
    else:
        await event.reply('Доступные режимы:\n.mode normal\n.mode busy\n.mode sleeping\n.mode meeting')

@client.on(events.NewMessage(pattern=r'\.online'))
async def set_online(event):
    global is_online
    is_online = True
    await event.reply('✅ Онлайн!')

@client.on(events.NewMessage(pattern=r'\.offline'))
async def set_offline(event):
    global is_online
    is_online = False
    await event.reply('🌙 Оффлайн!')

@client.on(events.NewMessage(pattern=r'\.status'))
async def check_status(event):
    status = "Онлайн" if is_online else "Оффлайн"
    mode_names = {"normal": "😊 Обычный", "busy": "😤 Занят", "sleeping": "😴 Сплю", "meeting": "🤝 Встреча"}
    moscow_time = get_time().strftime("%H:%M")
    
    text = f"""📊 **СТАТУС**

Состояние: {status}
Режим: {mode_names[current_mode]}
Время: {moscow_time} (МСК)
Фильтр: {FILTER_MODE}"""
    
    await event.reply(text)

@client.on(events.NewMessage(pattern=r'\.help'))
async def help_cmd(event):
    help_text = """📋 **ВСЕ КОМАНДЫ**

**Основные:**
.menu — меню
.status — статус
.online / .offline — смена статуса

**Режимы:**
.mode normal — обычный
.mode busy — занят
.mode sleeping — сплю
.mode meeting — встреча

**Инструменты:**
.stats — статистика
.analytics — аналитика
.remind минуты текст — напоминание

**Списки:**
.addwhite — белый список (ответом)
.addblack — чёрный список (ответом)

**Настройки:**
.filter — фильтрация
.db — проверить базу данных"""
    
    await event.reply(help_text)

@client.on(events.NewMessage(pattern=r'\.db'))
async def check_db(event):
    """Проверка базы данных"""
    try:
        total_users = len(db.get_top_users(1000))
        total_messages = db.get_total_messages()
        white_list = db.get_white_list()
        black_list = db.get_black_list()
        
        text = f"""🗄 **БАЗА ДАННЫХ**

Пользователей: {total_users}
Сообщений: {total_messages}
Белый список: {len(white_list)}
Чёрный список: {len(black_list)}
Статус: ✅ Работает"""
        
        await event.reply(text)
    except Exception as e:
        await event.reply(f'❌ Ошибка БД: {e}')

@client.on(events.NewMessage(pattern=r'\.filter'))
async def change_filter(event):
    global FILTER_MODE
    
    text = event.text.replace('.filter', '').strip().lower()
    
    if text in ["all", "bot_only", "whitelist"]:
        FILTER_MODE = text
        await event.reply(f'🔍 Фильтр изменён: {text}')
    else:
        await event.reply(f'Текущий фильтр: {FILTER_MODE}\n\nДля смены:\n.filter all — все\n.filter bot_only — только с ботом\n.filter whitelist — белый список')

@client.on(events.NewMessage(pattern=r'\.stats'))
async def show_stats(event):
    top_users = db.get_top_users(10)
    total_messages = db.get_total_messages()
    
    stats_text = f"📊 **СТАТИСТИКА**\n\n💬 Сообщений: {total_messages}\n\nТоп собеседников:\n"
    for user_id, name, count in top_users:
        stats_text += f"• {name}: {count} сообщ.\n"
    
    await send_to_topic(TOPIC_STATS, stats_text)
    await event.reply('📊 Отправлено в тему "Статистика"!')

@client.on(events.NewMessage(pattern=r'\.analytics'))
async def show_analytics(event):
    report = analytics.generate_report()
    await event.reply(report)

@client.on(events.NewMessage(pattern=r'\.remind'))
async def set_reminder(event):
    text = event.text.replace('.remind', '').strip()
    parts = text.split(' ', 1)
    
    if len(parts) >= 2:
        try:
            minutes = int(parts[0])
            reminder_text = parts[1]
            remind_at = (get_time() + timedelta(minutes=minutes)).isoformat()
            db.add_reminder(reminder_text, remind_at)
            await event.reply(f'⏰ Напомню через {minutes} мин: {reminder_text}')
        except ValueError:
            await event.reply('Формат: .remind минуты текст')

@client.on(events.NewMessage(pattern=r'\.addwhite'))
async def add_white(event):
    if event.reply_to_msg_id:
        reply_msg = await event.get_reply_message()
        db.set_white(reply_msg.sender_id, True)
        sender = await reply_msg.get_sender()
        await event.reply(f'✅ {sender.first_name} в белом списке!')
    else:
        await event.reply('Ответьте на сообщение командой .addwhite')

@client.on(events.NewMessage(pattern=r'\.addblack'))
async def add_black(event):
    if event.reply_to_msg_id:
        reply_msg = await event.get_reply_message()
        db.set_black(reply_msg.sender_id, True)
        sender = await reply_msg.get_sender()
        await event.reply(f'🚫 {sender.first_name} в чёрном списке!')
    else:
        await event.reply('Ответьте на сообщение командой .addblack')

# === ОСНОВНОЙ ОБРАБОТЧИК ===

@client.on(events.NewMessage(incoming=True))
async def handle_messages(event):
    global is_online, FILTER_MODE
    
    if event.out:
        return
    
    if event.text and event.text.startswith('.'):
        return
    
    if not event.is_private:
        return
    
    sender = await event.get_sender()
    sender_id = event.sender_id
    sender_name = sender.first_name if sender.first_name else "Неизвестный"
    
    # Безопасность
    if security.is_banned(sender_id):
        return
    
    if not security.check_rate_limit(sender_id):
        logger.warning(f"Флуд от {sender_name}")
        return
    
    # База данных
    db.add_user(sender_id, sender_name)
    db.add_message(sender_id, event.text)
    
    # Фильтрация
    white_list = db.get_white_list()
    black_list = db.get_black_list()
    
    if sender_id in black_list:
        return
    
    category = smart_filter.get_message_category(sender_id, event.text)
    
    # Белый список
    if sender_id in white_list or category == "important":
        await send_to_topic(TOPIC_IMPORTANT, f'⚡️ **ВАЖНОЕ!**\n\nОт: {sender_name}\nТекст: {event.text}\n🕐 {get_time().strftime("%H:%M")}')
        if not is_online:
            await event.reply(f'⚡️ {sender_name}, сообщение помечено как важное!')
        return
    
    # Спам
    if category == "spam":
        db.set_black(sender_id, True)
        logger.info(f"Спам от {sender_name}")
        return
    
    # Обычная обработка
    if not is_online:
        await event.reply(get_auto_reply(sender_name))
        await send_to_topic(TOPIC_INCOMING, f'📩 **Входящее**\n\nОт: {sender_name}\nТекст: {event.text}\n🕐 {get_time().strftime("%H:%M")}')
    else:
        await send_to_topic(TOPIC_INCOMING, f'🔔 **Сообщение**\n\nОт: {sender_name}\nТекст: {event.text}\n🕐 {get_time().strftime("%H:%M")}')

# === ЗАПУСК ===

async def main():
    await client.start()
    logger.info("✅ Бот запущен!")
    logger.info(f"📁 Группа: {GROUP_ID}")
    logger.info(f"🔍 Фильтр: {FILTER_MODE}")
    
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())