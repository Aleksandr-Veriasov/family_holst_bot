from telegram import ReplyKeyboardMarkup

# Клавиатура главного меню
main_menu = ReplyKeyboardMarkup(
    [
        ['📄 Калькулятор стоимости'],
        ['🖼 Примеры работ'],
        ['👤 Связаться с менеджером']
    ],
    resize_keyboard=True
)