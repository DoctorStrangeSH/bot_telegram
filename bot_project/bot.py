import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

logging.basicConfig(level=logging.INFO)

TOKEN = "8942069919:AAGmpcV-hzhzlAPlOMMt5rBW_q-1mYwBEmA"
YOUR_USER_ID = 542094552

bot = Bot(token=TOKEN)
dp = Dispatcher()

is_online = False

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Привет! Я работаю на Railway! 🎉")

@dp.message(Command("offline"))
async def cmd_offline(message: types.Message):
    global is_online
    if message.from_user.id == YOUR_USER_ID:
        is_online = False
        await message.answer("🌙 Оффлайн! Автоответчик включен.")

@dp.message(Command("online"))
async def cmd_online(message: types.Message):
    global is_online
    if message.from_user.id == YOUR_USER_ID:
        is_online = True
        await message.answer("✅ Онлайн!")

@dp.message(Command("status"))
async def cmd_status(message: types.Message):
    status = "Онлайн" if is_online else "Оффлайн"
    await message.answer(f"Статус: {status}")

@dp.message()
async def handle_all(message: types.Message):
    if message.from_user.id != YOUR_USER_ID:
        if not is_online:
            await message.answer(f"😴 [Автоответчик]\n{message.from_user.full_name}, я оффлайн!")
        await bot.send_message(YOUR_USER_ID, f"🔔 Сообщение от {message.from_user.full_name}: {message.text}")

async def main():
    print("Бот запущен на Railway!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())