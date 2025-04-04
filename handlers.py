import datetime
from aiogram.dispatcher import FSMContext # type: ignore
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton # type: ignore
from aiogram.dispatcher.filters.state import State, StatesGroup # type: ignore
from keyboards import main_keyboard, routes_keyboard
from admin import send_request_to_admin

# Состояния для FSM (Finite State Machine)
class Form(StatesGroup):
    route = State()
    date = State()
    passport_data = State()

# Команда /start
async def send_welcome(message: Message):
    await message.reply("Привет! Я помогу вам отправить запрос на поиск авиабилетов.", reply_markup=main_keyboard)

# Обработка кнопки "Отправить запрос"
async def send_request(message: Message):
    await message.reply("Выберите маршрут:", reply_markup=routes_keyboard)
    await Form.route.set()  # Устанавливаем состояние "route"

# Обработка маршрута
async def process_route(message: Message, state: FSMContext):
    route = message.text.strip()
    try:
        origin, destination = route.split('–')
        origin, destination = origin.strip(), destination.strip()
    except ValueError:
        await message.reply("Произошла ошибка при обработке маршрута.")
        return

    await state.update_data(route=route, origin=origin, destination=destination)
    await message.reply("Введите дату вылета в формате ДД.ММ.ГГГГ (например, 01.11.2023):")
    await Form.date.set()  # Устанавливаем состояние "date"

# Обработка даты
async def process_date(message: Message, state: FSMContext):
    date = message.text
    if not is_valid_date(date):
        await message.reply("Неверный формат даты. Пожалуйста, используйте формат ДД.ММ.ГГГГ.")
        return

    await state.update_data(date=date)
    data = await state.get_data()

    # Отправляем запрос администратору
    await send_request_to_admin(message, data)

    await message.reply("✅ Ваш запрос отправлен администратору. Ожидайте ответа.")
    await state.finish()

# Валидация даты
def is_valid_date(date_str):
    try:
        datetime.strptime(date_str, "%d.%m.%Y")
        return True
    except ValueError:
        return False

# Регистрация обработчиков
def register_handlers(dp):
    from aiogram.dispatcher.filters import Text # type: ignore
    dp.register_message_handler(send_welcome, commands=['start'])
    dp.register_message_handler(send_request, Text(equals="Отправить запрос"))
    dp.register_message_handler(process_route, state=Form.route)
    dp.register_message_handler(process_date, state=Form.date)