# secretary.py
import asyncio
import logging
from datetime import datetime, timezone, timedelta
from telethon import TelegramClient, events, Button
from telethon.sessions import StringSession

from config import *
from database import db
from filters import smart_filter
from scheduler import Scheduler
from analytics import analytics
from keyboards import *
from security import security
from integrations import weather_api, currency_api

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
FILTER_MODE = "all"  # all, bot_only, whitelist

def get_time():
    return datetime.now(MOSCOW_TZ)

def get_auto_reply(name):
    hour = get_time().hour
    
    mode_replies = {
        "normal": {
            (5, 12): f"☀️ Доброе утро, {name}! Sherlock скоро ответит.",
            (12, 17): f"👨‍💻 Добрый день, {name}! Sherlock на связи.",
            (17, 23): f"🌆 Добрый вечер, {name}! Sherlock отошёл.",
            (0, 5): f"🌙 Ночь! Sherlock спит. Не будить!",
        },
        "busy": {
            (5, 23): f"😤 {name}, Sherlock очень занят!",
            (0, 5): f"😤 {name}, даже ночью занят!",
        },
        "sleeping": {
            (5, 23): f"😴 {name}, Sherlock спит.",
            (0, 5): f"😴 {name}, Sherlock крепко спит!",
        },
        "meeting": {
            (5, 23): f"🤝 {name}, Sherlock на встрече.",
            (0, 5): f"🤝 {name}, встреча...",
        },
    }
    
    for (start, end), reply in mode_replies[current_mode].items():
        if start <= hour < end or (start == 0 and hour < end):
            return reply
    
    return f"Привет, {name}! Sherlock ответит позже."

async def send_to_topic(topic_id, message):
    try:
        await client.send_message(GROUP_ID, message, reply_to=topic_id)
        logger.info(f"Отправлено в тему {topic_id}")
    except Exception as e:
        logger.error(f"Ошибка отправки: {e}")

# Инициализация планировщика
scheduler = Scheduler(client, db, send_to_topic)

# === КОМАНДЫ ===

@client.on(events.NewMessage(pattern=r'\.menu'))
async def show_menu(event):
    await event.reply('🎛 **Главное меню:**', buttons=get_main_keyboard())

@client.on(events.NewMessage(pattern=r'\.settings'))
async def show_settings(event):
    await event.reply('⚙️ **Настройки:**', buttons=get_settings_keyboard())

@client.on(events.NewMessage(pattern=r'\.online'))
async def set_online(event):
    global is_online
    is_online = True
    await event.reply('✅ Онлайн!', buttons=get_main_keyboard())

@client.on(events.NewMessage(pattern=r'\.offline'))
async def set_offline(event):
    global is_online
    is_online = False
    await event.reply('🌙 Оффлайн!', buttons=get_main_keyboard())

@client.on(events.NewMessage(pattern=r'\.status'))
async def check_status(event):
    status = "Онлайн" if is_online else "Оффлайн"
    mode_names = {"normal": "😊 Обычный", "busy": "😤 Занят", "sleeping": "😴 Сплю", "meeting": "🤝 Встреча"}
    moscow_time = get_time().strftime("%H:%M")
    
    text = f"📊 Статус: {status}\n🎭 Режим: {mode_names[current_mode]}\n🕐 Москва: {moscow_time}\n🔍 Фильтр: {FILTER_MODE}"
    await event.reply(text, buttons=get_main_keyboard())

@client.on(events.NewMessage(pattern=r'\.help'))
async def help_cmd(event):
    help_text = """📋 **Все команды:**

**Основные:**
`.menu` — меню
`.status` — статус
`.online` / `.offline` — смена статуса

**Фильтры:**
`.filter` — настройка фильтрации
`.addwhite` — белый список
`.addblack` — чёрный список

**Инструменты:**
`.stats` — статистика
`.analytics` — аналитика
`.remind` — напоминание
`.weather` — погода
`.currency` — курсы валют

**Настройки:**
`.settings` — меню настроек
`.schedule` — расписание"""
    
    await event.reply(help_text, buttons=get_main_keyboard())

@client.on(events.NewMessage(pattern=r'\.filter'))
async def change_filter(event):
    global FILTER_MODE
    
    text = event.text.replace('.filter', '').strip().lower()
    
    if text in ["all", "bot_only", "whitelist"]:
        FILTER_MODE = text
        await event.reply(f'🔍 Фильтр изменён на: {text}')
    else:
        filters = {
            "all": "Все сообщения",
            "bot_only": "Только с ботом",
            "whitelist": "Только белый список"
        }
        current = filters.get(FILTER_MODE, "Неизвестно")
        await event.reply(f'🔍 Текущий фильтр: {current}\n\nДля смены: .filter all | bot_only | whitelist')

@client.on(events.NewMessage(pattern=r'\.stats'))
async def show_stats(event):
    top_users = db.get_top_users(10)
    total_messages = db.get_total_messages()
    
    stats_text = f"📊 **Статистика:**\n\n💬 Всего сообщений: {total_messages}\n\nТоп собеседников:\n"
    for user_id, name, count in top_users:
        stats_text += f"• {name}: {count} сообщ.\n"
    
    await send_to_topic(TOPIC_STATS, stats_text)
    await event.reply('📊 Статистика отправлена!')

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
            await event.reply(f'⏰ Напомню через {minutes} мин.')
        except ValueError:
            await event.reply('Формат: .remind минуты текст')

@client.on(events.NewMessage(pattern=r'\.weather'))
async def get_weather_cmd(event):
    city = event.text.replace('.weather', '').strip() or "Moscow"
    weather = await weather_api.get_weather(city)
    await event.reply(weather)

@client.on(events.NewMessage(pattern=r'\.currency'))
async def get_currency_cmd(event):
    rates = await currency_api.get_currency_message()
    await event.reply(rates)

@client.on(events.NewMessage(pattern=r'\.addwhite'))
async def add_white(event):
    if event.reply_to_msg_id:
        reply_msg = await event.get_reply_message()
        db.set_white(reply_msg.sender_id, True)
        sender = await reply_msg.get_sender()
        await event.reply(f'✅ {sender.first_name} в белом списке!')

@client.on(events.NewMessage(pattern=r'\.addblack'))
async def add_black(event):
    if event.reply_to_msg_id:
        reply_msg = await event.get_reply_message()
        db.set_black(reply_msg.sender_id, True)
        sender = await reply_msg.get_sender()
        await event.reply(f'🚫 {sender.first_name} в чёрном списке!')

# === ОБРАБОТКА КНОПОК ===

@client.on(events.CallbackQuery)
async def handle_buttons(event):
    global is_online, current_mode, FILTER_MODE
    
    data = event.data.decode()
    
    if data == "online":
        is_online = True
        await event.edit('✅ Онлайн!', buttons=get_main_keyboard())
    elif data == "offline":
        is_online = False
        await event.edit('🌙 Оффлайн!', buttons=get_main_keyboard())
    elif data == "status":
        status = "Онлайн" if is_online else "Оффлайн"
        await event.edit(f'📊 Статус: {status}', buttons=get_main_keyboard())
    elif data == "mode":
        await event.edit('🎭 Режимы:', buttons=get_mode_keyboard())
    elif data == "settings":
        await event.edit('⚙️ Настройки:', buttons=get_settings_keyboard())
    elif data == "analytics":
        report = analytics.generate_report()
        await event.edit(report[:1000], buttons=get_main_keyboard())
    elif data == "back":
        await event.edit('🎛 Меню:', buttons=get_main_keyboard())
    elif data.startswith("mode_"):
        current_mode = data.replace("mode_", "")
        mode_names = {"normal": "😊 Обычный", "busy": "😤 Занят", "sleeping": "😴 Сплю", "meeting": "🤝 Встреча"}
        await event.edit(f'Режим: {mode_names[current_mode]}', buttons=get_main_keyboard())
    elif data.startswith("filter_"):
        FILTER_MODE = data.replace("filter_", "")
        await event.edit(f'🔍 Фильтр: {FILTER_MODE}', buttons=get_main_keyboard())

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
        logger.info(f"Спам от {sender_name}, добавлен в чёрный список")
        return
    
    # Фильтр по режиму
    if FILTER_MODE == "bot_only" and sender_id not in db.get_white_list():
        return
    
    if FILTER_MODE == "whitelist" and sender_id not in white_list:
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
    
    # Запускаем планировщик
    await scheduler.start()
    
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())