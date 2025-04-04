from aiogram import Router, F  # Используем F для фильтров
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command  # Добавляем импорт Command
from keyboards import main_keyboard, routes_keyboard
from admin import send_request_to_admin
from datetime import datetime

# Создаем роутер
router = Router()

# Состояния для FSM
class Form(StatesGroup):
    route = State()
    date = State()
    passport_data = State()

# Команда /start
@router.message(Command('start'))  # Используем Command вместо commands
async def send_welcome(message: Message):
    await message.reply("Привет! Я помогу вам отправить запрос на поиск авиабилетов.", reply_markup=main_keyboard)

# Обработка кнопки "Отправить запрос"
@router.message(F.text == "Отправить запрос")  # Используем F.text для текстовых фильтров
async def send_request(message: Message, state: FSMContext):
    await message.reply("Выберите маршрут:", reply_markup=routes_keyboard)
    await state.set_state(Form.route)  # Устанавливаем состояние "route"

# Обработка маршрута
@router.message(Form.route)
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
    await state.set_state(Form.date)  # Устанавливаем состояние "date"

# Обработка даты
@router.message(Form.date)
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
    await state.clear()  # Очищаем состояние

# Валидация даты
def is_valid_date(date_str):
    try:
        datetime.strptime(date_str, "%d.%m.%Y")
        return True
    except ValueError:
        return False