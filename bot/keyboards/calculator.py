from telegram import ReplyKeyboardMarkup
from bot.prices import AVAILABLE_SIZES, EXTRA_OPTIONS, STYLE_OPTIONS
from bot.utils.helpers import chunked


# Клавиатуры для выборо размеров
size_keyboard = ReplyKeyboardMarkup(
    chunked(AVAILABLE_SIZES, 2),
    resize_keyboard=True,
    one_time_keyboard=True
)
# Клавиатура для выбора стиля
style_keyboard = ReplyKeyboardMarkup(
    chunked(STYLE_OPTIONS, 2),
    resize_keyboard=True,
    one_time_keyboard=True
)
# Клавиатура для выбора дополнительных опций
option_keyboard = ReplyKeyboardMarkup(
    chunked(list(EXTRA_OPTIONS.keys()), 2) + [['Готово']],
    resize_keyboard=True
)
