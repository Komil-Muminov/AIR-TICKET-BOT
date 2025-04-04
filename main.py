from aiogram import Bot, Dispatcher
from aiogram.types import Message
from handlers import router  # Используем Router вместо register_handlers

# Токен вашего бота
API_TOKEN = '7656597937:AAEMbl4CgeWNpCQS3dseLdrYExDRXlhoiA4'

# Создаем экземпляр бота
bot = Bot(token=API_TOKEN)

# Создаем диспетчер и подключаем роутер
dp = Dispatcher()
dp.include_router(router)

# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())