import asyncio  # ← ВОТ ЭТО ДОБАВЬ ПЕРВОЙ СТРОКОЙ
from telethon import TelegramClient

API_ID = 37376910
API_HASH = "fb904e19f44d327aaad824ba0d01d381"

client = TelegramClient('session', API_ID, API_HASH)

async def main():
    await client.start()
    print('Авторизация успешна!')
    print('Теперь можно загружать на Railway')

asyncio.run(main())