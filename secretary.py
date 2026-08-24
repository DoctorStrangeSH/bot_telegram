from telethon import TelegramClient, events
from telethon.sessions import StringSession
import asyncio

API_ID = 37376910
API_HASH = "fb904e19f44d327aaad824ba0d01d381"

SESSION_STRING = "1ApWapzMBu53lyW3dwKs05w6mLe-ycWEcgzChNf4Ud4sDlWBbgrjI3jWvM_a7F4TKdUTsuojQpy7YTXV7NZCs2vOtkgkgPLIoj70wE84E3qZEEXkO5PdfjU9HX16waA1Gvw6dcfhoMe9htGEiEKzu7UiKGOsMy75dyp1Q5LVYkbh7FVk9655zfSehAXLSMyLiGp9M-XG3ybcoc5j_W-zooESNbGVGBnqok7pBXcculdVHi6_PqPpp_SB-dmJwQTNmvy7uafebwqaRk8Ed5Il0tRx9SKtozQAhAn-32cICUs8jb193coYHE20QcMwOmht3X7Ylso85dkU9Vf3xgBJQYPi7KYgnLbE="

client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

is_online = False

@client.on(events.NewMessage(pattern=r'\.offline'))
async def set_offline(event):
    global is_online
    is_online = False
    await event.reply('🌙 Оффлайн! Автоответчик включен.')

@client.on(events.NewMessage(pattern=r'\.online'))
async def set_online(event):
    global is_online
    is_online = True
    await event.reply('✅ Онлайн!')

@client.on(events.NewMessage(pattern=r'\.status'))
async def check_status(event):
    status = "Онлайн" if is_online else "Оффлайн"
    await event.reply(f'Статус: {status}')

@client.on(events.NewMessage(incoming=True))
async def auto_reply(event):
    global is_online
    
    if event.out:
        return
    
    if event.text and event.text.startswith('.'):
        return
    
    if event.is_private:
        sender = await event.get_sender()
        sender_name = sender.first_name if sender.first_name else "Неизвестный"
        
        if not is_online:
            await event.reply(f'😴 [Автоответчик]\n{sender_name}, я оффлайн!')
            await client.send_message('me', f'📩 Сообщение от {sender_name}: {event.text}')
        else:
            await client.send_message('me', f'🔔 Сообщение от {sender_name}: {event.text}')

async def main():
    await client.start()
    print('✅ Юзербот запущен!')
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
