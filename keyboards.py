from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# Клавиатура с основными командами
main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Отправить запрос")]
    ],
    resize_keyboard=True
)

# Клавиатура для выбора Да/Нет
yes_no_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Да"), KeyboardButton(text="Нет")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

# Клавиатура с популярными маршрутами
routes_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Душанбе – Москва"), KeyboardButton(text="Москва – Душанбе")],
        [KeyboardButton(text="Ташкент – Душанбе"), KeyboardButton(text="Душанбе – Ташкент")],
        [KeyboardButton(text="Москва – Ташкент"), KeyboardButton(text="Ташкент – Москва")],
        [KeyboardButton(text="Душанбе – Стамбул"), KeyboardButton(text="Стамбул – Душанбе")],
        [KeyboardButton(text="Ташкент – Стамбул"), KeyboardButton(text="Стамбул – Ташкент")],
        [KeyboardButton(text="Москва – Стамбул"), KeyboardButton(text="Стамбул – Москва")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

# Создание клавиатуры для выбора билета
def create_ticket_selection_keyboard(tickets):
    buttons = []
    for i, ticket in enumerate(tickets):
        buttons.append([InlineKeyboardButton(text=f"Билет {i+1}: {ticket['summary']}", callback_data=f"select_ticket_{i}")])
    
    buttons.append([InlineKeyboardButton(text="Отмена", callback_data="cancel_selection")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# Клавиатура для подтверждения
confirm_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Подтвердить", callback_data="confirm"),
            InlineKeyboardButton(text="Отменить", callback_data="cancel")
        ]
    ]
)

# Клавиатура для пропуска загрузки скана паспорта
skip_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Пропустить")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)