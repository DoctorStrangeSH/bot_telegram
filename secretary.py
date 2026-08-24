from telethon import TelegramClient, events, Button
from telethon.sessions import StringSession
import asyncio
from datetime import datetime, timezone, timedelta
import random
import json

API_ID = 37376910
API_HASH = "fb904e19f44d327aaad824ba0d01d381"

SESSION_STRING = "1ApWapzMBu53lyW3dwKs05w6mLe-ycWEcgzChNf4Ud4sDlWBbgrjI3jWvM_a7F4TKdUTsuojQpy7YTXV7NZCs2vOtkgkgPLIoj70wE84E3qZEEXkO5PdfjU9HX16waA1Gvw6dcfhoMe9htGEiEKzu7UiKGOsMy75dyp1Q5LVYkbh7FVk9655zfSehAXLSMyLiGp9M-XG3ybcoc5j_W-zooESNbGVGBnqok7pBXcculdVHi6_PqPpp_SB-dmJwQTNmvy7uafebwqaRk8Ed5Il0tRx9SKtozQAhAn-32cICUs8jb193coYHE20QcMwOmht3X7Ylso85dkU9Vf3xgBJQYPi7KYgnLbE="

client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

# Московское время
MOSCOW_TZ = timezone(timedelta(hours=3))

# Статусы и режимы
is_online = False
current_mode = "normal"  # normal, busy, sleeping, meeting
white_list = []
black_list = []
message_stats = {}
custom_commands = {}
reminders = []

# Режимы и их описания
modes = {
    "normal": "😊 Обычный режим",
    "busy": "😤 Занят",
    "sleeping": "😴 Сплю",
    "meeting": "🤝 На встрече",
}

# Умные ответы
smart_replies = {
    "привет": ["Привет! 👋", "Здравствуйте!", "Добрый день!"],
    "как дела": ["Всё отлично! 😊", "Нормально, а у вас?", "Работаю!"],
    "спасибо": ["Пожалуйста! 😊", "Всегда рад помочь!"],
    "пока": ["До свидания! 👋", "Всего доброго!"],
    "срочно": ["⚡️ Срочное! Передаю немедленно!"],
}

# Гифки
gifs = [
    "https://media.giphy.com/media/3o7abKhOpu0NwenH3O/giphy.gif",
    "https://media.giphy.com/media/l0HlNaQ6gWfllcjDO/giphy.gif",
]

def get_moscow_time():
    return datetime.now(MOSCOW_TZ)

def get_time_of_day():
    hour = get_moscow_time().hour
    if 5 <= hour < 12:
        return "morning"
    elif 12 <= hour < 17:
        return "day"
    elif 17 <= hour < 23:
        return "evening"
    else:
        return "night"

def get_auto_reply(name):
    time_of_day = get_time_of_day()
    mode_replies = {
        "normal": {
            "morning": f"☀️ Доброе утро, {name}! Sherlock скоро ответит.",
            "day": f"👨‍💻 Добрый день, {name}! Sherlock занят, но на связи.",
            "evening": f"🌆 Добрый вечер, {name}! Sherlock отошёл ненадолго.",
            "night": f"🌙 Ночь! Sherlock спит. До 9:00 не будить!",
        },
        "busy": {
            "morning": f"😤 {name}, Sherlock очень занят! Не отвлекать!",
            "day": f"😤 {name}, Sherlock на важном деле!",
            "evening": f"😤 {name}, Sherlock работает! Позже!",
            "night": f"😤 {name}, даже ночью занят!",
        },
        "sleeping": {
            "morning": f"😴 {name}, Sherlock ещё спит...",
            "day": f"😴 {name}, Sherlock спит. Это не опечатка.",
            "evening": f"😴 {name}, Sherlock уснул. Не будить!",
            "night": f"😴 {name}, Sherlock крепко спит!",
        },
        "meeting": {
            "morning": f"🤝 {name}, Sherlock на утренней встрече.",
            "day": f"🤝 {name}, Sherlock на встрече. Ответит после.",
            "evening": f"🤝 {name}, Sherlock на вечерней встрече.",
            "night": f"🤝 {name}, встреча затянулась...",
        },
    }
    return mode_replies[current_mode][time_of_day]

def find_smart_reply(text):
    if not text:
        return None
    text_lower = text.lower()
    for keyword, replies in smart_replies.items():
        if keyword in text_lower:
            return random.choice(replies)
    return None

# Кнопки для управления
def get_main_keyboard():
    return [
        [Button.inline("✅ Онлайн", b"online"), Button.inline("🌙 Оффлайн", b"offline")],
        [Button.inline("📊 Статус", b"status"), Button.inline("📋 Помощь", b"help")],
    ]

def get_mode_keyboard():
    return [
        [Button.inline("😊 Обычный", b"mode_normal"), Button.inline("😤 Занят", b"mode_busy")],
        [Button.inline("😴 Сплю", b"mode_sleeping"), Button.inline("🤝 Встреча", b"mode_meeting")],
    ]

# Команды
@client.on(events.NewMessage(pattern=r'\.menu'))
async def show_menu(event):
    await event.reply('🎛 Главное меню:', buttons=get_main_keyboard())

@client.on(events.NewMessage(pattern=r'\.mode'))
async def show_modes(event):
    await event.reply('🎭 Выберите режим:', buttons=get_mode_keyboard())

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
    global is_online, current_mode
    status = "Онлайн" if is_online else "Оффлайн"
    moscow_time = get_moscow_time().strftime("%H:%M")
    mode_name = modes[current_mode]
    
    text = f"📊 Статус: {status}\n🎭 Режим: {mode_name}\n🕐 Москва: {moscow_time}"
    await event.reply(text, buttons=get_main_keyboard())

@client.on(events.NewMessage(pattern=r'\.help'))
async def help_cmd(event):
    help_text = """📋 **Команды бота:**

**.menu** — показать меню с кнопками
**.online** — включить онлайн
**.offline** — включить автоответчик
**.mode** — выбрать режим
**.status** — проверить статус
**.stats** — статистика
**.remind** — напоминание
**.addwhite** — белый список
**.addblack** — чёрный список
**.addcmd** — своя команда
**.gif** — случайная гифка
**.help** — это меню"""
    
    await event.reply(help_text, buttons=get_main_keyboard())

@client.on(events.NewMessage(pattern=r'\.stats'))
async def show_stats(event):
    if not message_stats:
        await event.reply('📊 Нет сообщений.')
        return
    
    stats_text = "📊 Топ собеседников:\n\n"
    sorted_stats = sorted(message_stats.items(), key=lambda x: x[1]['count'], reverse=True)
    
    for user_id, data in sorted_stats[:10]:
        stats_text += f"• {data['name']}: {data['count']} сообщ.\n"
    
    await event.reply(stats_text)

@client.on(events.NewMessage(pattern=r'\.gif'))
async def send_gif(event):
    random_gif = random.choice(gifs)
    await event.reply(file=random_gif)

@client.on(events.NewMessage(pattern=r'\.addwhite'))
async def add_white(event):
    global white_list
    if event.reply_to_msg_id:
        reply_msg = await event.get_reply_message()
        if reply_msg.sender_id not in white_list:
            white_list.append(reply_msg.sender_id)
            sender = await reply_msg.get_sender()
            await event.reply(f'✅ {sender.first_name} в белом списке!')
    else:
        await event.reply('Ответьте на сообщение командой .addwhite')

@client.on(events.NewMessage(pattern=r'\.addblack'))
async def add_black(event):
    global black_list
    if event.reply_to_msg_id:
        reply_msg = await event.get_reply_message()
        if reply_msg.sender_id not in black_list:
            black_list.append(reply_msg.sender_id)
            sender = await reply_msg.get_sender()
            await event.reply(f'🚫 {sender.first_name} в чёрном списке!')
    else:
        await event.reply('Ответьте на сообщение командой .addblack')

@client.on(events.NewMessage(pattern=r'\.addcmd'))
async def add_custom_command(event):
    global custom_commands
    text = event.text.replace('.addcmd', '').strip()
    if '|' in text:
        parts = text.split('|')
        cmd = parts[0].strip().lower()
        reply = parts[1].strip()
        custom_commands[cmd] = reply
        await event.reply(f'✅ Команда .{cmd} создана!')
    else:
        await event.reply('Формат: .addcmd команда | ответ')

@client.on(events.NewMessage(pattern=r'\.remind'))
async def set_reminder(event):
    # Формат: .remind 30 текст напоминания
    text = event.text.replace('.remind', '').strip()
    parts = text.split(' ', 1)
    
    if len(parts) >= 2:
        try:
            minutes = int(parts[0])
            reminder_text = parts[1]
            
            await event.reply(f'⏰ Напоминание через {minutes} мин: {reminder_text}')
            
            async def send_reminder():
                await asyncio.sleep(minutes * 60)
                await client.send_message('me', f'⏰ НАПОМИНАНИЕ:\n{reminder_text}')
            
            asyncio.create_task(send_reminder())
        except ValueError:
            await event.reply('Формат: .remind минуты текст\nНапример: .remind 30 Позвонить маме')
    else:
        await event.reply('Формат: .remind минуты текст')

# Обработка нажатий кнопок
@client.on(events.CallbackQuery)
async def handle_buttons(event):
    global is_online, current_mode
    
    data = event.data.decode()
    
    if data == b"online":
        is_online = True
        await event.edit('✅ Онлайн!', buttons=get_main_keyboard())
    elif data == b"offline":
        is_online = False
        await event.edit('🌙 Оффлайн!', buttons=get_main_keyboard())
    elif data == b"status":
        status = "Онлайн" if is_online else "Оффлайн"
        await event.edit(f'📊 Статус: {status}', buttons=get_main_keyboard())
    elif data == b"help":
        await event.edit('📋 Команды в описании!', buttons=get_main_keyboard())
    elif data == b"mode_normal":
        current_mode = "normal"
        await event.edit('😊 Режим: Обычный', buttons=get_mode_keyboard())
    elif data == b"mode_busy":
        current_mode = "busy"
        await event.edit('😤 Режим: Занят', buttons=get_mode_keyboard())
    elif data == b"mode_sleeping":
        current_mode = "sleeping"
        await event.edit('😴 Режим: Сплю', buttons=get_mode_keyboard())
    elif data == b"mode_meeting":
        current_mode = "meeting"
        await event.edit('🤝 Режим: На встрече', buttons=get_mode_keyboard())

# Основной обработчик
@client.on(events.NewMessage(incoming=True))
async def auto_reply(event):
    global is_online, white_list, black_list, message_stats, current_mode
    
    if event.out:
        return
    
    if event.text and event.text.startswith('.'):
        cmd = event.text[1:].split()[0].lower()
        if cmd in custom_commands:
            await event.reply(custom_commands[cmd])
        return
    
    if not event.is_private:
        return
    
    sender = await event.get_sender()
    sender_name = sender.first_name if sender.first_name else "Неизвестный"
    sender_id = event.sender_id
    
    # Статистика
    if sender_id not in message_stats:
        message_stats[sender_id] = {"name": sender_name, "count": 0}
    message_stats[sender_id]["count"] += 1
    
    # Чёрный список
    if sender_id in black_list:
        return
    
    # Белый список
    if sender_id in white_list:
        await client.send_message('me', f'⚡️ ВАЖНОЕ от {sender_name}:\n{event.text}')
        if not is_online:
            await event.reply(f'⚡️ {sender_name}, вы в белом списке!')
        return
    
    # Умные ответы
    smart_reply = find_smart_reply(event.text)
    
    if not is_online:
        if smart_reply:
            await event.reply(smart_reply)
        else:
            reply = get_auto_reply(sender_name)
            await event.reply(reply)
        
        await client.send_message('me', f'📩 От {sender_name}:\n{event.text}')
    else:
        if smart_reply:
            await event.reply(smart_reply)
        await client.send_message('me', f'🔔 От {sender_name}:\n{event.text}')

# Утренние/вечерние уведомления
async def scheduled_messages():
    while True:
        now = get_moscow_time()
        
        # В 9:00 отправляем утреннее сообщение
        if now.hour == 9 and now.minute == 0:
            await client.send_message('me', '☀️ Доброе утро! Проверьте сообщения!')
            await asyncio.sleep(60)
        
        # В 23:00 напоминаем про ночной режим
        if now.hour == 23 and now.minute == 0:
            await client.send_message('me', '🌙 Время спать! Включите .offline')
            await asyncio.sleep(60)
        
        await asyncio.sleep(30)

async def main():
    await client.start()
    print('✅ Юзербот запущен!')
    print(f'🕐 Московское время: {get_moscow_time().strftime("%H:%M")}')
    print('🎭 Режимы, кнопки, напоминания активированы!')
    
    # Запускаем планировщик
    asyncio.create_task(scheduled_messages())
    
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
