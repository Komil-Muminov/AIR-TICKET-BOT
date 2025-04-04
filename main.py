from aiogram import Bot, Dispatcher # type: ignore
from aiogram.utils import executor # type: ignore
from handlers import register_handlers

# Токен вашего бота
API_TOKEN = '7656597937:AAEMbl4CgeWNpCQS3dseLdrYExDRXlhoiA4'

# Создаем экземпляр бота
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Регистрируем обработчики
register_handlers(dp)

# Запуск бота
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)