from aiogram.fsm.state import StatesGroup, State

class Form(StatesGroup):
    route = State()  # Состояние для выбора маршрута
    date = State()   # Состояние для ввода даты
    confirm_details = State()  # Подтверждение выбранных деталей
    waiting_for_tickets = State()  # Ожидание вариантов билетов от админа
    admin_sending_tickets = State()  # Админ отправляет варианты билетов
    select_ticket = State()  # Выбор билета из списка
    passport_data = State()  # Ввод паспортных данных
    uploading_passport_scan = State()  # Загрузка скана паспорта
    admin_sending_eticket = State()  # Админ отправляет электронный билет
    confirm_eticket = State()  # Подтверждение электронного билета