from telethon import TelegramClient, events
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
TOPIC_INCOMING = 2  # Входящие
TOPIC_REMINDERS = 3  # Напоминания
TOPIC_STATS = 4  # Статистика
TOPIC_IMPORTANT = 5  # Важные

# Статусы
is_online = False
white_list = []
black_list = []
message_stats = {}

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
    replies = {
        "morning": f"☀️ Доброе утро, {name}! Sherlock скоро ответит.",
        "day": f"👨‍💻 Добрый день, {name}! Sherlock на связи.",
        "evening": f"🌆 Добрый вечер, {name}! Sherlock отошёл.",
        "night": f"🌙 Ночь! Sherlock спит. Не будить!",
    }
    return replies[time_of_day]

# Функция отправки в тему
async def send_to_topic(topic_id, message):
    """Отправляет сообщение в указанную тему группы"""
    try:
        await client.send_message(
            GROUP_ID,
            message,
            reply_to=topic_id
        )
        print(f"✅ Отправлено в тему {topic_id}")
    except Exception as e:
        print(f"❌ Ошибка отправки в тему: {e}")
        # Фолбэк: в "Избранное"
        await client.send_message('me', message)

# Команды
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
    global is_online
    status = "Онлайн" if is_online else "Оффлайн"
    moscow_time = get_moscow_time().strftime("%H:%M")
    await event.reply(f"📊 Статус: {status}\n🕐 Москва: {moscow_time}")

@client.on(events.NewMessage(pattern=r'\.help'))
async def help_cmd(event):
    help_text = """📋 **Команды бота:**

**.online** — включить онлайн
**.offline** — включить автоответчик
**.status** — проверить статус
**.stats** — статистика в группу
**.remind** — напоминание
**.addwhite** — белый список
**.addblack** — чёрный список
**.help** — это меню"""
    
    await event.reply(help_text)

# Команда .stats
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

# Команда .remind
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

# Команда .addwhite
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

# Команда .addblack
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

# Основной обработчик
@client.on(events.NewMessage(incoming=True))
async def auto_reply(event):
    global is_online, white_list, black_list, message_stats
    
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
            f'⚡️ **ВАЖНОЕ сообщение!**\n\nОт: {sender_name}\nТекст: {event.text}\n🕐 {get_moscow_time().strftime("%H:%M")}'
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

# Планировщик — ежедневные отчёты
async def daily_report():
    while True:
        now = get_moscow_time()
        
        # В 9:00 — утренний отчёт
        if now.hour == 9 and now.minute == 0:
            report = f"☀️ **Утренний отчёт**\n\n📅 {now.strftime('%d.%m.%Y')}\n🕐 {now.strftime('%H:%M')}\n📊 Собеседников: {len(message_stats)}"
            await send_to_topic(TOPIC_STATS, report)
            await asyncio.sleep(60)
        
        # В 23:00 — вечерний отчёт
        if now.hour == 23 and now.minute == 0:
            report = f"🌙 **Вечерний отчёт**\n\n📊 Всего собеседников: {len(message_stats)}\n"
            sorted_stats = sorted(message_stats.items(), key=lambda x: x[1]['count'], reverse=True)
            for user_id, data in sorted_stats[:5]:
                report += f"• {data['name']}: {data['count']} сообщ.\n"
            await send_to_topic(TOPIC_STATS, report)
            await asyncio.sleep(60)
        
        await asyncio.sleep(30)

async def main():
    await client.start()
    print('✅ Юзербот запущен!')
    print(f'📁 Группа: {GROUP_ID}')
    print('📋 Темы: Входящие(2), Напоминания(3), Статистика(4), Важные(5)')
    
    # Запускаем планировщик
    asyncio.create_task(daily_report())
    
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
