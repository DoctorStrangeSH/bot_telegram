from telethon import TelegramClient, events
from telethon.sessions import StringSession
import asyncio
from datetime import datetime
import random

API_ID = 37376910
API_HASH = "fb904e19f44d327aaad824ba0d01d381"

SESSION_STRING = "1ApWapzMBu53lyW3dwKs05w6mLe-ycWEcgzChNf4Ud4sDlWBbgrjI3jWvM_a7F4TKdUTsuojQpy7YTXV7NZCs2vOtkgkgPLIoj70wE84E3qZEEXkO5PdfjU9HX16waA1Gvw6dcfhoMe9htGEiEKzu7UiKGOsMy75dyp1Q5LVYkbh7FVk9655zfSehAXLSMyLiGp9M-XG3ybcoc5j_W-zooESNbGVGBnqok7pBXcculdVHi6_PqPpp_SB-dmJwQTNmvy7uafebwqaRk8Ed5Il0tRx9SKtozQAhAn-32cICUs8jb193coYHE20QcMwOmht3X7Ylso85dkU9Vf3xgBJQYPi7KYgnLbE="

client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

# Статусы
is_online = False
is_sleeping = False  # Ночной режим

# Списки людей
white_list = []  # Важные люди
black_list = []  # Игнорируемые

# Приветственные фразы
greetings = [
    "👋 Привет! Я секретарь Sherlock Holmes.",
    "🤖 Здравствуйте! Я бот-ассистент.",
    "😊 Добро пожаловать! Я на связи.",
]

# Случайные гифки (можно добавить свои URL)
gifs = [
    "https://media.giphy.com/media/3o7abKhOpu0NwenH3O/giphy.gif",
    "https://media.giphy.com/media/l0HlNaQ6gWfllcjDO/giphy.gif",
]

# Функция определения времени суток
def get_time_of_day():
    hour = datetime.now().hour
    if 5 <= hour < 12:
        return "morning"
    elif 12 <= hour < 17:
        return "day"
    elif 17 <= hour < 23:
        return "evening"
    else:
        return "night"

# Генерация автоответа по времени
def get_auto_reply(name):
    time_of_day = get_time_of_day()
    
    replies = {
        "morning": f"☀️ Доброе утро, {name}! Sherlock сейчас на связи. Отвечу в ближайшее время!",
        "day": f"👨‍💻 Добрый день, {name}! Sherlock занят, но скоро ответит.",
        "evening": f"🌆 Добрый вечер, {name}! Sherlock отошёл ненадолго.",
        "night": f"🌙 Сейчас ночь! Sherlock спит. Не будите до 9:00!",
    }
    
    return replies[time_of_day]

# Команда .online
@client.on(events.NewMessage(pattern=r'\.online'))
async def set_online(event):
    global is_online
    is_online = True
    await event.reply('✅ Онлайн! Автоответчик выключен.')

# Команда .offline
@client.on(events.NewMessage(pattern=r'\.offline'))
async def set_offline(event):
    global is_online
    is_online = False
    await event.reply('🌙 Оффлайн! Автоответчик включен.')

# Команда .status
@client.on(events.NewMessage(pattern=r'\.status'))
async def check_status(event):
    global is_online
    status = "Онлайн ✅" if is_online else "Оффлайн 🌙"
    time_now = datetime.now().strftime("%H:%M")
    await event.reply(f'📊 Статус: {status}\n🕐 Время: {time_now}')

# Команда .help
@client.on(events.NewMessage(pattern=r'\.help'))
async def help_cmd(event):
    help_text = """📋 **Команды бота:**

**.online** — включить онлайн
**.offline** — включить автоответчик
**.status** — проверить статус
**.addwhite** — добавить в белый список
**.addblack** — добавить в чёрный список
**.gif** — отправить случайную гифку
**.help** — показать это меню"""
    
    await event.reply(help_text)

# Команда .gif
@client.on(events.NewMessage(pattern=r'\.gif'))
async def send_gif(event):
    random_gif = random.choice(gifs)
    await event.reply(file=random_gif)

# Команда .addwhite
@client.on(events.NewMessage(pattern=r'\.addwhite'))
async def add_white(event):
    global white_list
    if event.reply_to_msg_id:
        reply_msg = await event.get_reply_message()
        if reply_msg.sender_id not in white_list:
            white_list.append(reply_msg.sender_id)
            await event.reply(f'✅ Добавлен в белый список!')
    else:
        await event.reply('Ответьте на сообщение человека командой .addwhite')

# Команда .addblack
@client.on(events.NewMessage(pattern=r'\.addblack'))
async def add_black(event):
    global black_list
    if event.reply_to_msg_id:
        reply_msg = await event.get_reply_message()
        if reply_msg.sender_id not in black_list:
            black_list.append(reply_msg.sender_id)
            await event.reply(f'🚫 Добавлен в чёрный список!')
    else:
        await event.reply('Ответьте на сообщение человека командой .addblack')

# Основной обработчик
@client.on(events.NewMessage(incoming=True))
async def auto_reply(event):
    global is_online, white_list, black_list
    
    # Игнорируем свои сообщения
    if event.out:
        return
    
    # Игнорируем команды
    if event.text and event.text.startswith('.'):
        return
    
    # Работаем только в личных чатах
    if not event.is_private:
        return
    
    sender = await event.get_sender()
    sender_name = sender.first_name if sender.first_name else "Неизвестный"
    sender_id = event.sender_id
    
    # Проверяем чёрный список
    if sender_id in black_list:
        return  # Игнорируем
    
    # Проверяем белый список
    if sender_id in white_list:
        await client.send_message('me', f'⚡️ ВАЖНОЕ сообщение от {sender_name}:\n{event.text}')
        if not is_online:
            await event.reply(f'⚡️ {sender_name}, вы в белом списке! Sherlock уведомлён срочно!')
        return
    
    # Обычная обработка
    if not is_online:
        reply = get_auto_reply(sender_name)
        await event.reply(reply)
        await client.send_message('me', f'📩 Сообщение от {sender_name}:\n{event.text}')
    else:
        await client.send_message('me', f'🔔 Сообщение от {sender_name}:\n{event.text}')

# Запуск
async def main():
    await client.start()
    print('✅ Юзербот запущен!')
    print('📋 Команды: .online, .offline, .status, .help, .gif')
    print('👥 Белый/чёрный список: .addwhite, .addblack (ответом на сообщение)')
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
