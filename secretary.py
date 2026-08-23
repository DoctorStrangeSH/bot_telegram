from telethon import TelegramClient, events
import asyncio

API_ID = 37376910
API_HASH = "fb904e19f44d327aaad824ba0d01d381"

client = TelegramClient('session', API_ID, API_HASH)

is_online = False

@client.on(events.NewMessage(pattern=r'\.offline'))
async def set_offline(event):
    global is_online
    is_online = False
    await event.reply('🌙 Оффлайн!')

@client.on(events.NewMessage(pattern=r'\.online'))
async def set_online(event):
    global is_online
    is_online = True
    await event.reply('✅ Онлайн!')

@client.on(events.NewMessage(incoming=True))
async def auto_reply(event):
    global is_online
    
    if event.out or not event.is_private:
        return
    
    if event.text and event.text.startswith('.'):
        return
    
    sender = await event.get_sender()
    
    if not is_online:
        await event.reply(f'😴 Автоответчик: я оффлайн!')
        await client.send_message('me', f'📩 Сообщение от {sender.first_name}: {event.text}')

async def main():
    await client.start()
    print('Юзербот запущен!')
    await client.run_until_disconnected()

asyncio.run(main())