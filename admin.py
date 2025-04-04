from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message

# ID администратора
ADMIN_CHAT_ID = 5657657583  # Замените на ваш реальный ID

# Бот для отправки сообщений администратору
bot = Bot(token='7656597937:AAEMbl4CgeWNpCQS3dseLdrYExDRXlhoiA4')  # Замените на ваш токен

# Отправка запроса администратору
async def send_request_to_admin(message: Message, data):
    user_id = message.from_user.id
    route = data['route']
    date = data['date']

    # Формируем текст запроса
    request_text = f"✈️ Новый запрос на поиск билета:\n" \
                   f"Маршрут: {route}\n" \
                   f"Дата: {date}\n" \
                   f"ID пользователя: {user_id}"

    # Кнопка для подтверждения
    confirm_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Подтвердить", callback_data=f"confirm_{user_id}")]
    ])

    # Отправляем запрос администратору
    await bot.send_message(ADMIN_CHAT_ID, request_text, reply_markup=confirm_keyboard)