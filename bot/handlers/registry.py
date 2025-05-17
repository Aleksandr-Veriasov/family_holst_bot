from telegram.ext import (
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

from bot.handlers.calculator import (
    CHOOSING_FACE_COUNT,
    CHOOSING_OPTIONS,
    CHOOSING_SIZE,
    CHOOSING_STYLE,
    face_count_chosen,
    options_chosen,
    size_chosen,
    start_calculator,
    style_chosen,
)
from bot.handlers.contact import (
    WAITING_FOR_MESSAGE,
    forward_to_manager,
    request_contact,
)
from bot.handlers.examples import (
    CHOOSING_EXAMPLE_STYLE,
    send_example_images,
    show_example_styles,
)
from bot.handlers.start import start_command


def register_handlers(app):
    # Команды
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(MessageHandler(
        filters.Regex('^🔙 В главное меню$'), start_command
    ))

    # FSM калькулятор
    calculator_conv = ConversationHandler(
        entry_points=[MessageHandler(
            filters.Regex('^📄 Калькулятор стоимости$'), start_calculator
        )],
        states={
            CHOOSING_SIZE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, size_chosen)
            ],
            CHOOSING_STYLE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, style_chosen)
            ],
            CHOOSING_FACE_COUNT: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND, face_count_chosen
                )
            ],
            CHOOSING_OPTIONS: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, options_chosen)
            ],
        },
        fallbacks=[],
        allow_reentry=True
    )
    app.add_handler(calculator_conv)

    # FSM примеры работ
    examples_conv = ConversationHandler(
        entry_points=[MessageHandler(
            filters.Regex('^🖼 Примеры работ$'), show_example_styles
        )],
        states={
            CHOOSING_EXAMPLE_STYLE: [MessageHandler(
                filters.TEXT & ~filters.COMMAND, send_example_images
            )]
        },
        fallbacks=[],
        allow_reentry=True
    )
    app.add_handler(examples_conv)

    # FSM связь с менеджером
    contact_conv = ConversationHandler(
        entry_points=[MessageHandler(
            filters.Regex('^👤 Связаться с менеджером$'), request_contact
        )],
        states={
            WAITING_FOR_MESSAGE: [MessageHandler(
                    filters.TEXT & ~filters.COMMAND, forward_to_manager
                )]
        },
        fallbacks=[],
        allow_reentry=True
    )
    app.add_handler(contact_conv)
