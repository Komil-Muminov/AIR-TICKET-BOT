from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Клавиатура с основными командами
main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Отправить запрос")]
    ],
    resize_keyboard=True
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