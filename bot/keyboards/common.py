from telegram import ReplyKeyboardMarkup

# Клавиатура перехода в главное меню
main_menu_button = ReplyKeyboardMarkup(
    [['🔙 В главное меню']],
    resize_keyboard=True,
    one_time_keyboard=True
)
