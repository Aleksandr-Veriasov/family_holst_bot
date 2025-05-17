from telegram import ReplyKeyboardMarkup
from bot.prices import STYLE_OPTIONS
from bot.utils.helpers import chunked


# Клавиатура для выбора стиля дизайна
style_keyboard = ReplyKeyboardMarkup(
    keyboard=chunked(STYLE_OPTIONS, 2),  # по 2 кнопки в строке
    resize_keyboard=True,
    one_time_keyboard=True
)
