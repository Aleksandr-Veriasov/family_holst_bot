import logging

from telegram import Message, Update
from telegram.ext import ContextTypes

from bot.keyboards.main_menu import main_menu
from bot.utils.decorators import ensure_message

logger = logging.getLogger(__name__)


@ensure_message
async def start_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    user = update.effective_user
    if user is None:
        logger.error('Пользователь не найден')
        return
    logger.info(f'Пользователь {user.id} ({user.first_name}) отправил /start')

    assert update.message is not None
    message: Message = update.message

    await message.reply_text(
        'Привет! Я помогу вам оформить заказ на портрет 🎨\n'
        'Выберите действие из меню ниже:',
        reply_markup=main_menu
    )
