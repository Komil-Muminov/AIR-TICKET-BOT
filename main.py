from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
import asyncio
import logging
import os

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Токен вашего бота
API_TOKEN = '7656597937:AAEMbl4CgeWNpCQS3dseLdrYExDRXlhoiA4'
# ID администратора
ADMIN_CHAT_ID = 5657657583

# Директория для сохранения загружаемых изображений
IMAGES_DIR = "uploaded_images"

# Создаем директорию, если она не существует
os.makedirs(IMAGES_DIR, exist_ok=True)

# Создаем экземпляры бота и диспетчера
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Импортируем роутеры после определения bot и dp
from handlers import setup_routers

# Настраиваем все роутеры
setup_routers(dp, bot, ADMIN_CHAT_ID)

# Запуск бота
async def main():

# Удаляем webhook, если он установлен
    await bot.delete_webhook(drop_pending_updates=True)

    # Начинаем поллинг
    await dp.start_polling(bot, skip_updates=True)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Бот остановлен!")