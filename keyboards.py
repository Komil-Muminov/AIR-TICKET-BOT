from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Клавиатура с основными командами
main_keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(
    KeyboardButton("Отправить запрос")
)

# Клавиатура с популярными маршрутами
routes_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2).add(
    KeyboardButton("Душанбе – Москва"),
    KeyboardButton("Москва – Душанбе"),
    KeyboardButton("Москва – Куляб"),
    KeyboardButton("Куляб – Москва"),
    KeyboardButton("Ташкент – Душанбе"),
    KeyboardButton("Душанбе – Ташкент"),
    KeyboardButton("Москва – Ташкент"),
    KeyboardButton("Ташкент – Москва"),
    KeyboardButton("Душанбе – Стамбул"),
    KeyboardButton("Стамбул – Душанбе"),
    KeyboardButton("Ташкент – Стамбул"),
    KeyboardButton("Стамбул – Ташкент"),
    KeyboardButton("Москва – Стамбул"),
    KeyboardButton("Стамбул – Москва")
)