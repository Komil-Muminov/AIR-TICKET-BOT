from aiogram import Router, F, types
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from states import Form
from keyboards import main_keyboard, routes_keyboard, create_ticket_selection_keyboard, confirm_keyboard, yes_no_keyboard
from datetime import datetime
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import os
import uuid
from aiogram.types import ReplyKeyboardMarkup

import json
import qrcode


# Инициализируем роутер
router = Router()

# Директория для сохранения загружаемых изображений
IMAGES_DIR = "uploaded_images"

# Создаем директорию, если она не существует
os.makedirs(IMAGES_DIR, exist_ok=True)

# Функция для проверки формата даты
def is_valid_date(date_str):
    try:
        datetime.strptime(date_str, "%d.%m.%Y")
        return True
    except ValueError:
        return False

# Обработчики команд
@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        "👋 Добро пожаловать в бот поиска авиабилетов!\n"
        "Нажмите на кнопку, чтобы начать.",
        reply_markup=main_keyboard
    )

@router.message(F.text == "Отправить запрос")
async def cmd_request(message: Message, state: FSMContext):
    await message.answer("Выберите маршрут:", reply_markup=routes_keyboard)
    await state.set_state(Form.route)

# Обработчики состояний
@router.message(Form.route)
async def process_route(message: Message, state: FSMContext):
    route = message.text
    await state.update_data(route=route)
    await message.answer("Введите дату в формате ДД.ММ.ГГГГ:")
    await state.set_state(Form.date)

@router.message(Form.date)
async def process_date(message: Message, state: FSMContext):
    date = message.text
    if not is_valid_date(date):
        await message.reply("Неверный формат даты. Пожалуйста, используйте формат ДД.ММ.ГГГГ.")
        return
    
    await state.update_data(date=date)
    
    # Здесь просим подтверждение маршрута и даты
    data = await state.get_data()
    await message.answer(
        f"Подтвердите выбранные данные:\n"
        f"Маршрут: {data['route']}\n"
        f"Дата: {data['date']}\n\n"
        f"Всё верно?",
        reply_markup=yes_no_keyboard
    )
    await state.set_state(Form.confirm_details)

@router.message(Form.confirm_details)
async def confirm_details(message: Message, state: FSMContext):
    if message.text.lower() == "да":
        # Отправляем запрос админу
        data = await state.get_data()
        user_id = message.from_user.id
        user_name = message.from_user.full_name
        
        # Формируем текст запроса
        request_text = (f"✈️ Новый запрос на поиск билета:\n"
                        f"Маршрут: {data['route']}\n"
                        f"Дата: {data['date']}\n"
                        f"Пользователь: {user_name} (ID: {user_id})")
        
        # Кнопка для подтверждения
        confirm_keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Отправить варианты билетов", callback_data=f"send_tickets_{user_id}")]
        ])
        
        # Отправляем запрос администратору
        await router.bot.send_message(router.admin_chat_id, request_text, reply_markup=confirm_keyboard)
        await message.reply("✅ Ваш запрос отправлен администратору. Ожидайте когда вам пришлют варианты билетов.")
        await state.set_state(Form.waiting_for_tickets)
    else:
        await message.answer("Запрос отменен. Вы можете начать заново.", reply_markup=main_keyboard)
        await state.clear()

# Обработчик callback от админа для отправки билетов
@router.callback_query(F.data.startswith("send_tickets_"))
async def handle_send_tickets(callback_query: CallbackQuery, state: FSMContext):
    user_id = int(callback_query.data.split('_')[2])
    
    # Сохраняем ID пользователя для дальнейшей работы
    await state.update_data(current_user_id=user_id)
    
    await callback_query.answer("Подготовка к отправке билетов...")
    await router.bot.send_message(
        callback_query.from_user.id,
        "Пожалуйста, отправьте список доступных билетов (файл, текст или изображение) для пользователя."
    )
    await state.set_state(Form.admin_sending_tickets)

# Обработчик получения билетов от админа
@router.message(Form.admin_sending_tickets)
async def process_admin_tickets(message: Message, state: FSMContext):
    data = await state.get_data()
    user_id = data.get('current_user_id')
    
    if not user_id:
        await message.answer("Ошибка: ID пользователя не найден.")
        return
    
    # Обрабатываем случай с файлом
    if message.document:
        file_id = message.document.file_id
        file = await router.bot.get_file(file_id)
        file_path = file.file_path
        downloaded_file = await router.bot.download_file(file_path)
        
        # Сохраняем информацию о файле
        await state.update_data(ticket_file_id=file_id, file_name=message.document.file_name)
        
        # Отправляем файл клиенту
        await router.bot.send_document(
            user_id, 
            document=file_id,
            caption="📄 Вот доступные варианты билетов. Хотите приобрести билет?",
            reply_markup=yes_no_keyboard
        )
    # Обрабатываем случай с изображением
    elif message.photo:
        # Получаем самое большое изображение (последнее в списке)
        photo = message.photo[-1]
        file_id = photo.file_id
        
        # Отправляем изображение клиенту
        await router.bot.send_photo(
            user_id,
            photo=file_id,
            caption="🖼️ Вот доступные варианты билетов на изображении. Хотите приобрести билет?",
            reply_markup=yes_no_keyboard
        )
    # Обрабатываем случай с текстом
    elif message.text:
        ticket_options = message.text
        await state.update_data(ticket_options=ticket_options)
        
        # Отправляем текст клиенту
        await router.bot.send_message(
            user_id,
            f"📋 Доступные варианты билетов:\n\n{ticket_options}\n\nХотите приобрести билет?",
            reply_markup=yes_no_keyboard
        )
    else:
        await message.answer("Пожалуйста, отправьте список билетов в виде текста, файла или изображения.")
        return
    
    await message.answer("Список билетов отправлен клиенту. Ожидайте ответа.")
    # Изменяем состояние клиента
    # Создаем временное состояние для клиента
    client_state = router.client_states.get(user_id, {})
    client_state['state'] = 'waiting_for_purchase_decision'
    router.client_states[user_id] = client_state

# Обработчик решения клиента о покупке
@router.message(lambda message: router.client_states.get(message.from_user.id, {}).get('state') == 'waiting_for_purchase_decision')
async def process_purchase_decision(message: Message, state: FSMContext):
    user_id = message.from_user.id
    
    if message.text.lower() == "да":
        await message.answer("Пожалуйста, введите данные паспорта (серия и номер):")
        
        # Обновляем состояние клиента
        client_state = router.client_states.get(user_id, {})
        client_state['state'] = 'entering_passport'
        router.client_states[user_id] = client_state
    else:
        await message.answer("Вы отказались от покупки билета. Спасибо за обращение.", reply_markup=main_keyboard)
        
        # Уведомляем админа
        admin_message = f"❌ Пользователь {message.from_user.full_name} (ID: {user_id}) отказался от покупки билета."
        await router.bot.send_message(router.admin_chat_id, admin_message)
        
        # Очищаем состояние клиента
        if user_id in router.client_states:
            del router.client_states[user_id]

@router.message(lambda message: router.client_states.get(message.from_user.id, {}).get('state') == 'entering_passport')
async def process_passport(message: Message, state: FSMContext):
    user_id = message.from_user.id
    client_state = router.client_states.get(user_id, {})

    passport_data = None
    scan_file_id = None
    scan_type = None  # 'photo' или 'document'

    if message.text:
        passport_data = message.text.strip()
    elif message.document:
        scan_file_id = message.document.file_id
        scan_type = "document"
    elif message.photo:
        scan_file_id = message.photo[-1].file_id
        scan_type = "photo"
    
    if not passport_data and not scan_file_id:
        await message.answer("Пожалуйста, введите данные паспорта текстом или отправьте скан.")
        return

    # Сохраняем введенные данные
    client_state['passport_data'] = passport_data or "(данные на скане)"
    client_state['passport_scan'] = {
        "file_id": scan_file_id,
        "type": scan_type
    } if scan_file_id else None
    client_state['state'] = 'waiting_for_eticket'
    router.client_states[user_id] = client_state

    await message.answer("Ваши данные отправлены администратору. Ожидайте оформления билета.")

    # Сообщение админу
    admin_text = (f"🛂 Пользователь {message.from_user.full_name} (ID: {user_id}) отправил паспортные данные:\n"
                  f"{client_state['passport_data']}\n")

    admin_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Отправить электронный билет", callback_data=f"send_eticket_{user_id}")]
    ])

    await router.bot.send_message(router.admin_chat_id, admin_text)

    if scan_file_id:
        if scan_type == "photo":
            await router.bot.send_photo(router.admin_chat_id, scan_file_id, reply_markup=admin_keyboard)
        else:
            await router.bot.send_document(router.admin_chat_id, scan_file_id, reply_markup=admin_keyboard)
    else:
        await router.bot.send_message(router.admin_chat_id, "Без скана паспорта.", reply_markup=admin_keyboard)


# Обработчик загрузки скана паспорта
@router.message(lambda message: router.client_states.get(message.from_user.id, {}).get('state') == 'uploading_passport_scan')
async def process_passport_scan(message: Message, state: FSMContext):
    user_id = message.from_user.id
    client_state = router.client_states.get(user_id, {})
    
    # Если пользователь решил пропустить загрузку
    if message.text and message.text.lower() == "пропустить":
        await message.answer("Ваши данные отправлены администратору. Ожидайте оформления билета.")
        
        # Уведомляем админа без скана
        admin_message = (f"🛂 Пользователь {message.from_user.full_name} (ID: {user_id}) отправил паспортные данные:\n"
                        f"{client_state.get('passport_data')}\n\n"
                        f"Пользователь не прикрепил скан паспорта.\n\n"
                        f"Пожалуйста, оформите билет и отправьте его пользователю.")
        
        admin_keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Отправить электронный билет", callback_data=f"send_eticket_{user_id}")]
        ])
        
        await router.bot.send_message(router.admin_chat_id, admin_message, reply_markup=admin_keyboard)
    
    # Если пользователь загрузил изображение
    elif message.photo:
        # Получаем самое большое изображение
        photo = message.photo[-1]
        file_id = photo.file_id
        
        # Загружаем фото
        file = await router.bot.get_file(file_id)
        file_path = file.file_path
        
        # Генерируем уникальное имя файла
        unique_filename = f"{uuid.uuid4()}.jpg"
        save_path = os.path.join(IMAGES_DIR, unique_filename)
        
        # Скачиваем файл
        downloaded_file = await router.bot.download_file(file_path, destination=save_path)
        
        await message.answer("Скан паспорта получен. Ваши данные отправлены администратору. Ожидайте оформления билета.")
        
        # Уведомляем админа и отправляем скан
        admin_message = (f"🛂 Пользователь {message.from_user.full_name} (ID: {user_id}) отправил паспортные данные:\n"
                        f"{client_state.get('passport_data')}\n\n"
                        f"Скан паспорта прикреплен ниже.\n\n"
                        f"Пожалуйста, оформите билет и отправьте его пользователю.")
        
        admin_keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Отправить электронный билет", callback_data=f"send_eticket_{user_id}")]
        ])
        
        # Отправляем сообщение и фото админу
        await router.bot.send_message(router.admin_chat_id, admin_message)
        await router.bot.send_photo(router.admin_chat_id, photo=file_id, reply_markup=admin_keyboard)
    
    # Если пользователь загрузил документ
    elif message.document:
        file_id = message.document.file_id
        
        await message.answer("Скан паспорта получен. Ваши данные отправлены администратору. Ожидайте оформления билета.")
        
        # Уведомляем админа и отправляем скан
        admin_message = (f"🛂 Пользователь {message.from_user.full_name} (ID: {user_id}) отправил паспортные данные:\n"
                        f"{client_state.get('passport_data')}\n\n"
                        f"Скан паспорта прикреплен ниже как документ.\n\n"
                        f"Пожалуйста, оформите билет и отправьте его пользователю.")
        
        admin_keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Отправить электронный билет", callback_data=f"send_eticket_{user_id}")]
        ])
        
        # Отправляем сообщение и документ админу
        await router.bot.send_message(router.admin_chat_id, admin_message)
        await router.bot.send_document(router.admin_chat_id, document=file_id, reply_markup=admin_keyboard)
    
    else:
        await message.answer("Пожалуйста, загрузите скан паспорта как изображение или документ, либо нажмите 'Пропустить'.")
        return
    
    # Обновляем состояние клиента
    client_state['state'] = 'waiting_for_eticket'
    router.client_states[user_id] = client_state

# Обработчик кнопки отправки электронного билета
@router.callback_query(F.data.startswith("send_eticket_"))
async def handle_send_eticket(callback_query: CallbackQuery, state: FSMContext):
    user_id = int(callback_query.data.split('_')[2])
    
    # Сохраняем ID пользователя для дальнейшей работы
    await state.update_data(current_user_id=user_id)
    
    await callback_query.answer("Подготовка к отправке электронного билета...")
    await router.bot.send_message(
        callback_query.from_user.id,
        "Пожалуйста, отправьте электронный билет (файл или изображение) для пользователя."
    )
    await state.set_state(Form.admin_sending_eticket)

# Обработчик получения электронного билета от админа
@router.message(Form.admin_sending_eticket)
async def process_admin_eticket(message: Message, state: FSMContext):
    data = await state.get_data()
    user_id = data.get('current_user_id')
    
    if not user_id:
        await message.answer("Ошибка: ID пользователя не найден.")
        return
    
    # Обрабатываем случай с файлом
    if message.document:
        file_id = message.document.file_id
        
        # Отправляем файл клиенту
        await router.bot.send_document(
            user_id, 
            document=file_id,
            caption="🎫 Вот ваш электронный билет. Пожалуйста, проверьте все данные. Билет верен?",
            reply_markup=yes_no_keyboard
        )
        
        await message.answer("Электронный билет отправлен клиенту. Ожидайте подтверждения.")
    
    # Обрабатываем случай с изображением
    elif message.photo:
        # Получаем самое большое изображение
        photo = message.photo[-1]
        file_id = photo.file_id
        
        # Отправляем изображение клиенту
        await router.bot.send_photo(
            user_id,
            photo=file_id,
            caption="🎫 Вот ваш электронный билет. Пожалуйста, проверьте все данные. Билет верен?",
            reply_markup=yes_no_keyboard
        )
        
        await message.answer("Электронный билет (изображение) отправлен клиенту. Ожидайте подтверждения.")
    
    else:
        await message.answer("Пожалуйста, отправьте электронный билет в виде файла или изображения.")
        return
    
    # Обновляем состояние клиента
    client_state = router.client_states.get(user_id, {})
    client_state['state'] = 'confirming_eticket'
    router.client_states[user_id] = client_state

# Обработчик подтверждения билета клиентом
@router.message(lambda message: router.client_states.get(message.from_user.id, {}).get('state') == 'confirming_eticket')
async def confirm_eticket(message: Message, state: FSMContext):
    user_id = message.from_user.id
    
    if message.text.lower() == "да":
        await message.answer("Спасибо! Ваш билет подтвержден. Приятного полета! ✈️", reply_markup=main_keyboard)
        
        # Уведомляем админа
        admin_message = f"✅ Пользователь {message.from_user.full_name} (ID: {user_id}) подтвердил получение билета. Заявка закрыта."
        await router.bot.send_message(router.admin_chat_id, admin_message)
    else:
        await message.answer("Вы указали, что с билетом есть проблемы. Администратор свяжется с вами для уточнения деталей.")
        
        # Уведомляем админа
        admin_message = f"⚠️ Пользователь {message.from_user.full_name} (ID: {user_id}) сообщил о проблеме с билетом. Требуется уточнение."
        await router.bot.send_message(router.admin_chat_id, admin_message)
    
    # Очищаем состояние клиента
    if user_id in router.client_states:
        del router.client_states[user_id]

# Добавляем обработчик для загрузки скриншотов в любой момент
@router.message(F.photo)
async def handle_image(message: Message):
    # Если мы не находимся в одном из специальных состояний для обработки изображений
    user_id = message.from_user.id
    client_state = router.client_states.get(user_id, {}).get('state')
    
    # Если у пользователя нет активного состояния для обработки изображений
    if not client_state or client_state not in ['uploading_passport_scan', 'confirming_eticket']:
        await message.answer("Получено изображение! Если вы хотите оформить билет, пожалуйста, нажмите 'Отправить запрос'.", 
                           reply_markup=main_keyboard)







# ---------------

# 1. Асинхронная обработка вложений
async def handle_file(message, file_id, file_name):
    file = await message.bot.get_file(file_id)
    file_path = file.file_path
    downloaded_file = await message.bot.download_file(file_path)
    # Асинхронно сохраняем файл на диск, если нужно
    with open(f"uploaded_files/{file_name}", "wb") as f:
        f.write(downloaded_file)
    return downloaded_file

# 2. Сохранение истории заявок
def save_request_to_history(request_data):
    try:
        with open('requests_history.json', 'r') as file:
            history = json.load(file)
    except FileNotFoundError:
        history = []
    
    history.append(request_data)
    
    with open('requests_history.json', 'w') as file:
        json.dump(history, file, indent=4)

# 3. Уведомления и фоллоу-ап
async def send_follow_up_notifications(user_id, message_text):
    await asyncio.sleep(10)  # Задержка между уведомлениями
    await bot.send_message(user_id, message_text)

# 4. Интеграция с календарем (кнопки inline)
def create_calendar_markup():
    markup = InlineKeyboardMarkup()
    for i in range(1, 32):  # Пример простого календаря на 31 день
        markup.add(InlineKeyboardButton(str(i), callback_data=f"day_{i}"))
    return markup

@router.message(Form.date)
async def process_date(message: Message, state: FSMContext):
    date = message.text
    if not is_valid_date(date):
        await message.reply("Неверный формат даты. Пожалуйста, используйте формат ДД.ММ.ГГГГ.")
        return

    # Отправляем календарь
    await message.answer("Выберите день из календаря:", reply_markup=create_calendar_markup())
    await state.set_state(Form.date_selected)

# 5. QR-код билета
async def generate_qr_code(ticket_data):
    qr = qrcode.make(ticket_data)
    qr_path = f"tickets/{uuid.uuid4()}.png"
    qr.save(qr_path)
    return qr_path

# 6. Автоформатирование текстов
def format_ticket_options(ticket_text):
    # Форматируем текст в виде списка с номерами
    formatted_text = ""
    tickets = ticket_text.split("\n")
    for idx, ticket in enumerate(tickets, 1):
        formatted_text += f"{bold(str(idx))}. {ticket}\n"
    return formatted_text

# Пример использования форматирования
@router.message(Form.admin_sending_tickets)
async def process_admin_tickets(message: Message, state: FSMContext):
    data = await state.get_data()
    user_id = data.get('current_user_id')

    if message.text:
        ticket_options = format_ticket_options(message.text)
        await router.bot.send_message(
            user_id,
            f"📋 Доступные варианты билетов:\n\n{ticket_options}\n\nХотите приобрести билет?",
            reply_markup=yes_no_keyboard
        )
    else:
        await message.answer("Пожалуйста, отправьте список билетов в виде текста.")

    await message.answer("Список билетов отправлен клиенту. Ожидайте ответа.")
    # Изменяем состояние клиента
    client_state = router.client_states.get(user_id, {})
    client_state['state'] = 'waiting_for_purchase_decision'
    router.client_states[user_id] = client_state

# Сохраняем запросы в историю и отправляем уведомления
@router.message(Form.confirm_details)
async def confirm_details(message: Message, state: FSMContext):
    if message.text.lower() == "да":
        data = await state.get_data()
        user_id = message.from_user.id
        user_name = message.from_user.full_name

        # Формируем текст запроса
        request_text = (f"✈️ Новый запрос на поиск билета:\n"
                        f"Маршрут: {data['route']}\n"
                        f"Дата: {data['date']}\n"
                        f"Пользователь: {user_name} (ID: {user_id})")

        # Сохраняем запрос в историю
        save_request_to_history(request_text)

        await message.reply("✅ Ваш запрос отправлен администратору. Ожидайте, когда вам пришлют варианты билетов.")

        # Отправляем уведомление пользователю через несколько минут
        await send_follow_up_notifications(user_id, "Не забывайте следить за вашим запросом. Администратор скоро ответит.")

        await state.set_state(Form.waiting_for_tickets)
    else:
        await message.answer("Запрос отменен. Вы можете начать заново.", reply_markup=main_keyboard)
        await state.clear()

# Функция для инициализации роутера с экземпляром бота
def setup_routers(dp, bot, admin_chat_id):
    # Сохраняем ID администратора в роутере
    router.admin_chat_id = admin_chat_id
    
    # Сохраняем экземпляр бота в роутере
    router.bot = bot
    
    # Создаем словарь для хранения состояний клиентов
    router.client_states = {}
    
    dp.include_router(router)