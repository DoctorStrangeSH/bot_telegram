from telethon import TelegramClient, events, Button
from telethon.sessions import StringSession
import asyncio
from datetime import datetime, timezone, timedelta
import random

API_ID = 37376910
API_HASH = "fb904e19f44d327aaad824ba0d01d381"

SESSION_STRING = "1ApWapzMBu53lyW3dwKs05w6mLe-ycWEcgzChNf4Ud4sDlWBbgrjI3jWvM_a7F4TKdUTsuojQpy7YTXV7NZCs2vOtkgkgPLIoj70wE84E3qZEEXkO5PdfjU9HX16waA1Gvw6dcfhoMe9htGEiEKzu7UiKGOsMy75dyp1Q5LVYkbh7FVk9655zfSehAXLSMyLiGp9M-XG3ybcoc5j_W-zooESNbGVGBnqok7pBXcculdVHi6_PqPpp_SB-dmJwQTNmvy7uafebwqaRk8Ed5Il0tRx9SKtozQAhAn-32cICUs8jb193coYHE20QcMwOmht3X7Ylso85dkU9Vf3xgBJQYPi7KYgnLbE="

client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

# Московское время
MOSCOW_TZ = timezone(timedelta(hours=3))

# ID группы и тем
GROUP_ID = 1004368107724
TOPIC_INCOMING = 2
TOPIC_REMINDERS = 3
TOPIC_STATS = 4
TOPIC_IMPORTANT = 5

# Статусы
is_online = False
current_mode = "normal"
white_list = []
black_list = []
message_stats = {}

# Режимы
modes = {
    "normal": "😊 Обычный",
    "busy": "😤 Занят",
    "sleeping": "😴 Сплю",
    "meeting": "🤝 На встрече",
}

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
    return mode_replies[current_mode][time_of_day]

# Функция отправки в тему
async def send_to_topic(topic_id, message):
    try:
        await client.send_message(GROUP_ID, message, reply_to=topic_id)
        print(f"✅ Отправлено в тему {topic_id}")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        await client.send_message('me', message)

# Кнопки
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

# === КОМАНДЫ ===

@client.on(events.NewMessage(pattern=r'\.menu'))
async def show_menu(event):
    await event.reply('🎛 **Главное меню:**', buttons=get_main_keyboard())

@client.on(events.NewMessage(pattern=r'\.mode'))
async def show_modes(event):
    await event.reply('🎭 **Выберите режим:**', buttons=get_mode_keyboard())

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
    mode_name = modes[current_mode]
    moscow_time = get_moscow_time().strftime("%H:%M")
    
    text = f"📊 Статус: {status}\n🎭 Режим: {mode_name}\n🕐 Москва: {moscow_time}"
    await event.reply(text, buttons=get_main_keyboard())

@client.on(events.NewMessage(pattern=r'\.help'))
async def help_cmd(event):
    help_text = """📋 **Все команды:**

**.menu** — меню с кнопками
**.mode** — выбрать режим
**.online** — включить онлайн
**.offline** — включить автоответчик
**.status** — проверить статус
**.stats** — статистика
**.remind** — напоминание
**.addwhite** — белый список
**.addblack** — чёрный список
**.gif** — случайная гифка
**.help** — это меню"""
    
    await event.reply(help_text, buttons=get_main_keyboard())

@client.on(events.NewMessage(pattern=r'\.stats'))
async def show_stats(event):
    if not message_stats:
        await event.reply('📊 Нет сообщений.')
        return
    
    stats_text = "📊 **Топ собеседников:**\n\n"
    sorted_stats = sorted(message_stats.items(), key=lambda x: x[1]['count'], reverse=True)
    
    for user_id, data in sorted_stats[:10]:
        stats_text += f"• {data['name']}: {data['count']} сообщ.\n"
    
    await send_to_topic(TOPIC_STATS, stats_text)
    await event.reply('📊 Статистика отправлена в группу!')

@client.on(events.NewMessage(pattern=r'\.remind'))
async def set_reminder(event):
    text = event.text.replace('.remind', '').strip()
    parts = text.split(' ', 1)
    
    if len(parts) >= 2:
        try:
            minutes = int(parts[0])
            reminder_text = parts[1]
            
            await event.reply(f'⏰ Напоминание через {minutes} мин: {reminder_text}')
            
            async def send_reminder():
                await asyncio.sleep(minutes * 60)
                await send_to_topic(
                    TOPIC_REMINDERS,
                    f'⏰ **НАПОМИНАНИЕ!**\n\n{reminder_text}\n\n🕐 {get_moscow_time().strftime("%H:%M")}'
                )
            
            asyncio.create_task(send_reminder())
        except ValueError:
            await event.reply('Формат: .remind минуты текст')
    else:
        await event.reply('Формат: .remind минуты текст')

@client.on(events.NewMessage(pattern=r'\.gif'))
async def send_gif(event):
    gifs = [
        "https://media.giphy.com/media/3o7abKhOpu0NwenH3O/giphy.gif",
        "https://media.giphy.com/media/l0HlNaQ6gWfllcjDO/giphy.gif",
    ]
    await event.reply(file=random.choice(gifs))

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

# Обработка кнопок
@client.on(events.CallbackQuery)
async def handle_buttons(event):
    global is_online, current_mode
    
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
    elif data == "help":
        await event.edit('📋 Команды в описании!', buttons=get_main_keyboard())
    elif data == "mode_normal":
        current_mode = "normal"
        await event.edit('😊 Режим: Обычный', buttons=get_mode_keyboard())
    elif data == "mode_busy":
        current_mode = "busy"
        await event.edit('😤 Режим: Занят', buttons=get_mode_keyboard())
    elif data == "mode_sleeping":
        current_mode = "sleeping"
        await event.edit('😴 Режим: Сплю', buttons=get_mode_keyboard())
    elif data == "mode_meeting":
        current_mode = "meeting"
        await event.edit('🤝 Режим: На встрече', buttons=get_mode_keyboard())

# Основной обработчик
@client.on(events.NewMessage(incoming=True))
async def auto_reply(event):
    global is_online, white_list, black_list, message_stats, current_mode
    
    if event.out:
        return
    
    if event.text and event.text.startswith('.'):
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
        await send_to_topic(
            TOPIC_IMPORTANT,
            f'⚡️ **ВАЖНОЕ!**\n\nОт: {sender_name}\nТекст: {event.text}\n🕐 {get_moscow_time().strftime("%H:%M")}'
        )
        if not is_online:
            await event.reply(f'⚡️ {sender_name}, вы в белом списке!')
        return
    
    # Обычные сообщения
    if not is_online:
        await event.reply(get_auto_reply(sender_name))
        await send_to_topic(
            TOPIC_INCOMING,
            f'📩 **Входящее**\n\nОт: {sender_name}\nТекст: {event.text}\n🕐 {get_moscow_time().strftime("%H:%M")}'
        )
    else:
        await send_to_topic(
            TOPIC_INCOMING,
            f'🔔 **Сообщение**\n\nОт: {sender_name}\nТекст: {event.text}\n🕐 {get_moscow_time().strftime("%H:%M")}'
        )

# Ежедневные отчёты
async def daily_report():
    while True:
        now = get_moscow_time()
        
        if now.hour == 9 and now.minute == 0:
            report = f"☀️ **Утренний отчёт**\n\n📅 {now.strftime('%d.%m.%Y')}\n📊 Собеседников: {len(message_stats)}"
            await send_to_topic(TOPIC_STATS, report)
            await asyncio.sleep(60)
        
        await asyncio.sleep(30)

async def main():
    await client.start()
    print('✅ Юзербот запущен!')
    print(f'📁 Группа: {GROUP_ID}')
    print('📋 Все команды активны!')
    
    asyncio.create_task(daily_report())
    
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
