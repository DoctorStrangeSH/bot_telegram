# secretary.py
import asyncio
import logging
from datetime import datetime
from telethon import TelegramClient, events, Button
from telethon.sessions import StringSession
import json
import os

from config import *

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Создание клиента
client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

# Состояние бота
class BotState:
    def __init__(self):
        self.is_online = False
        self.current_mode = "normal"
        self.white_list = set()
        self.black_list = set()
        self.message_stats = {}
        self.known_users = set()
        self.load_data()
    
    def load_data(self):
        """Загрузка данных из JSON"""
        try:
            if os.path.exists('bot_data.json'):
                with open('bot_data.json', 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.white_list = set(data.get('white_list', []))
                    self.black_list = set(data.get('black_list', []))
                    self.message_stats = data.get('message_stats', {})
                    self.known_users = set(data.get('known_users', []))
                    logger.info("✅ Данные загружены")
        except Exception as e:
            logger.error(f"Ошибка загрузки данных: {e}")
    
    def save_data(self):
        """Сохранение данных в JSON"""
        try:
            data = {
                'white_list': list(self.white_list),
                'black_list': list(self.black_list),
                'message_stats': self.message_stats,
                'known_users': list(self.known_users)
            }
            with open('bot_data.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Ошибка сохранения: {e}")

state = BotState()

# Вспомогательные функции
def get_time():
    return datetime.now(MOSCOW_TZ)

def get_time_of_day():
    hour = get_time().hour
    if 5 <= hour < 12:
        return "morning"
    elif 12 <= hour < 17:
        return "day"
    elif 17 <= hour < 23:
        return "evening"
    return "night"

def get_auto_reply(name):
    time_of_day = get_time_of_day()
    
    replies = {
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
    return replies[state.current_mode][time_of_day]

async def send_to_topic(topic_id, message):
    """Отправка сообщения в тему группы"""
    try:
        await client.send_message(GROUP_ID, message, reply_to=topic_id)
        logger.info(f"Отправлено в тему {topic_id}")
        return True
    except Exception as e:
        logger.error(f"Ошибка отправки в тему {topic_id}: {e}")
        return False

# Кнопки
def get_main_keyboard():
    return [
        [Button.inline("✅ Онлайн", b"online"), Button.inline("🌙 Оффлайн", b"offline")],
        [Button.inline("📊 Статус", b"status"), Button.inline("🎭 Режим", b"mode")],
    ]

def get_mode_keyboard():
    return [
        [Button.inline("😊 Обычный", b"mode_normal"), Button.inline("😤 Занят", b"mode_busy")],
        [Button.inline("😴 Сплю", b"mode_sleeping"), Button.inline("🤝 Встреча", b"mode_meeting")],
    ]

# Фильтрация сообщений
def should_process_message(sender_id):
    """Определяет, нужно ли обрабатывать сообщение"""
    # Чёрный список — всегда игнорируем
    if sender_id in state.black_list:
        return False, "blacklist"
    
    # Белый список — всегда обрабатываем
    if sender_id in state.white_list:
        return True, "whitelist"
    
    # Режимы фильтрации
    if FILTER_MODE == "all":
        return True, "all"
    
    elif FILTER_MODE == "bot_only":
        if sender_id in state.known_users:
            return True, "known"
        return False, "unknown"
    
    elif FILTER_MODE == "whitelist":
        return False, "not_whitelisted"
    
    return True, "default"

# === КОМАНДЫ ===

@client.on(events.NewMessage(pattern=r'\.menu'))
async def show_menu(event):
    await event.reply('🎛 **Главное меню:**', buttons=get_main_keyboard())

@client.on(events.NewMessage(pattern=r'\.mode'))
async def show_modes(event):
    await event.reply('🎭 **Режимы:**', buttons=get_mode_keyboard())

@client.on(events.NewMessage(pattern=r'\.online'))
async def set_online(event):
    state.is_online = True
    await event.reply('✅ Онлайн!', buttons=get_main_keyboard())

@client.on(events.NewMessage(pattern=r'\.offline'))
async def set_offline(event):
    state.is_online = False
    await event.reply('🌙 Оффлайн!', buttons=get_main_keyboard())

@client.on(events.NewMessage(pattern=r'\.status'))
async def check_status(event):
    status = "Онлайн" if state.is_online else "Оффлайн"
    mode_names = {"normal": "😊 Обычный", "busy": "😤 Занят", "sleeping": "😴 Сплю", "meeting": "🤝 Встреча"}
    moscow_time = get_time().strftime("%H:%M")
    
    text = f"📊 Статус: {status}\n🎭 Режим: {mode_names[state.current_mode]}\n🕐 Москва: {moscow_time}"
    await event.reply(text, buttons=get_main_keyboard())

@client.on(events.NewMessage(pattern=r'\.help'))
async def help_cmd(event):
    help_text = """📋 **Команды:**

`.menu` — меню
`.mode` — режимы
`.online` — онлайн
`.offline` — оффлайн
`.status` — статус
`.stats` — статистика
`.remind` — напоминание
`.addwhite` — белый список (ответом)
`.addblack` — чёрный список (ответом)
`.filter` — режим фильтрации
`.help` — помощь"""
    
    await event.reply(help_text, buttons=get_main_keyboard())

@client.on(events.NewMessage(pattern=r'\.filter'))
async def change_filter(event):
    filters = {
        "all": "Все сообщения",
        "bot_only": "Только с ботом",
        "whitelist": "Только белый список"
    }
    
    current = filters.get(FILTER_MODE, "Неизвестно")
    await event.reply(f'🔍 Текущий фильтр: {current}\n\nДля смены: .filter all | bot_only | whitelist')

@client.on(events.NewMessage(pattern=r'\.stats'))
async def show_stats(event):
    if not state.message_stats:
        await event.reply('📊 Нет данных.')
        return
    
    stats_text = "📊 **Топ собеседников:**\n\n"
    sorted_stats = sorted(state.message_stats.items(), key=lambda x: x[1]['count'], reverse=True)
    
    for user_id, data in sorted_stats[:10]:
        stats_text += f"• {data['name']}: {data['count']} сообщ.\n"
    
    await send_to_topic(TOPIC_STATS, stats_text)
    await event.reply('📊 Статистика отправлена!')

@client.on(events.NewMessage(pattern=r'\.remind'))
async def set_reminder(event):
    text = event.text.replace('.remind', '').strip()
    parts = text.split(' ', 1)
    
    if len(parts) >= 2:
        try:
            minutes = int(parts[0])
            reminder_text = parts[1]
            
            await event.reply(f'⏰ Напомню через {minutes} мин.')
            
            async def send_reminder():
                await asyncio.sleep(minutes * 60)
                await send_to_topic(TOPIC_REMINDERS, f'⏰ **НАПОМИНАНИЕ!**\n\n{reminder_text}')
            
            asyncio.create_task(send_reminder())
        except ValueError:
            await event.reply('Формат: .remind минуты текст')
    else:
        await event.reply('Формат: .remind минуты текст')

@client.on(events.NewMessage(pattern=r'\.addwhite'))
async def add_white(event):
    if event.reply_to_msg_id:
        reply_msg = await event.get_reply_message()
        state.white_list.add(reply_msg.sender_id)
        state.save_data()
        sender = await reply_msg.get_sender()
        await event.reply(f'✅ {sender.first_name} в белом списке!')
    else:
        await event.reply('Ответьте на сообщение командой .addwhite')

@client.on(events.NewMessage(pattern=r'\.addblack'))
async def add_black(event):
    if event.reply_to_msg_id:
        reply_msg = await event.get_reply_message()
        state.black_list.add(reply_msg.sender_id)
        state.save_data()
        sender = await reply_msg.get_sender()
        await event.reply(f'🚫 {sender.first_name} в чёрном списке!')
    else:
        await event.reply('Ответьте на сообщение командой .addblack')

# === ОБРАБОТКА КНОПОК ===

@client.on(events.CallbackQuery)
async def handle_buttons(event):
    data = event.data.decode()
    
    if data == "online":
        state.is_online = True
        await event.edit('✅ Онлайн!', buttons=get_main_keyboard())
    elif data == "offline":
        state.is_online = False
        await event.edit('🌙 Оффлайн!', buttons=get_main_keyboard())
    elif data == "status":
        status = "Онлайн" if state.is_online else "Оффлайн"
        await event.edit(f'📊 Статус: {status}', buttons=get_main_keyboard())
    elif data == "mode":
        await event.edit('🎭 Выберите режим:', buttons=get_mode_keyboard())
    elif data.startswith("mode_"):
        state.current_mode = data.replace("mode_", "")
        mode_names = {"normal": "😊 Обычный", "busy": "😤 Занят", "sleeping": "😴 Сплю", "meeting": "🤝 Встреча"}
        await event.edit(f'Режим: {mode_names[state.current_mode]}', buttons=get_main_keyboard())

# === ОСНОВНОЙ ОБРАБОТЧИК ===

@client.on(events.NewMessage(incoming=True))
async def handle_messages(event):
    if event.out:
        return
    
    if event.text and event.text.startswith('.'):
        return
    
    if not event.is_private:
        return
    
    sender = await event.get_sender()
    sender_id = event.sender_id
    sender_name = sender.first_name if sender.first_name else "Неизвестный"
    
    # Обновляем статистику
    if sender_id not in state.message_stats:
        state.message_stats[sender_id] = {"name": sender_name, "count": 0}
    state.message_stats[sender_id]["count"] += 1
    state.save_data()
    
    # Проверяем фильтрацию
    should_process, reason = should_process_message(sender_id)
    
    if not should_process:
        logger.info(f"Сообщение отфильтровано ({reason}): {sender_name}")
        return
    
    # Белый список
    if reason == "whitelist":
        await send_to_topic(TOPIC_IMPORTANT, f'⚡️ **ВАЖНОЕ!**\n\nОт: {sender_name}\nТекст: {event.text}\n🕐 {get_time().strftime("%H:%M")}')
        if not state.is_online:
            await event.reply(f'⚡️ {sender_name}, вы в белом списке!')
        return
    
    # Обычная обработка
    if not state.is_online:
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