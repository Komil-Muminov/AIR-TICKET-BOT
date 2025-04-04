from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# ID администратора
ADMIN_CHAT_ID = 5657657583

# Отправка запроса администратору
async def send_request_to_admin(message: types.Message, data):
    user_id = message.from_user.id
    route = data['route']
    date = data['date']

    # Формируем текст запроса
    request_text = f"✈️ Новый запрос на поиск билета:\n" \
                   f"Маршрут: {route}\n" \
                   f"Дата: {date}\n" \
                   f"ID пользователя: {user_id}"

    # Кнопка для подтверждения
    confirm_keyboard = InlineKeyboardMarkup().add(
        InlineKeyboardButton("Подтвердить", callback_data=f"confirm_{user_id}")
    )

    # Отправляем запрос администратору
    await bot.send_message(ADMIN_CHAT_ID, request_text, reply_markup=confirm_keyboard)

# Обработка подтверждения от администратора
async def handle_admin_confirmation(callback_query: types.CallbackQuery):
    user_id = int(callback_query.data.split("_")[1])
    await bot.send_message(user_id, "✅ Администратор нашел билет. Если вы согласны, нажмите 'Купить'.",
                           reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(
                               KeyboardButton("Купить")
                           ))
    await callback_query.answer("Запрос подтвержден.")

# Обработка покупки
async def handle_purchase(message: types.Message):
    await message.reply("Введите свои паспортные данные в формате: ФИО, номер паспорта, дата рождения (ДД.ММ.ГГГГ).")
    await Form.passport_data.set()

# Обработка паспортных данных
async def process_passport_data(message: types.Message, state: FSMContext):
    passport_data = message.text
    user_id = message.from_user.id

    # Отправляем данные администратору
    await bot.send_message(ADMIN_CHAT_ID, f"📋 Паспортные данные пользователя {user_id}:\n{passport_data}")

    await message.reply("✅ Данные отправлены. Ожидайте электронный билет.")
    await state.finish()