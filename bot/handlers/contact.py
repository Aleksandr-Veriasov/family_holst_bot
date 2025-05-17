import logging
from datetime import datetime, time

import pytz
from telegram import Update, Message
from telegram.ext import ContextTypes, ConversationHandler

from bot.config import ADMIN_ID
from bot.utils.decorators import ensure_message

logger = logging.getLogger(__name__)

WAITING_FOR_MESSAGE = 200


def is_within_working_hours() -> bool:
    now = datetime.now(pytz.timezone('Europe/Moscow')).time()
    return time(10, 0) <= now < time(19, 0)


def format_user_message(user, text: str) -> str:
    username = user.username or user.first_name or 'Пользователь'
    return (
        f'📩 Новое сообщение от пользователя @{username} '
        f'(ID: {user.id}):\n\n{text}'
    )


@ensure_message
async def request_contact(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    assert update.message is not None
    message: Message = update.message

    await message.reply_text(
        '✉️ Пожалуйста, напишите ваш вопрос, мы передадим его менеджеру.'
    )
    return WAITING_FOR_MESSAGE


@ensure_message
async def forward_to_manager(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    assert update.message is not None
    user = update.effective_user
    if not user:
        logger.warning('⚠️ Не удалось получить пользователя из update.')
        await update.message.reply_text('Произошла ошибка. Попробуйте позже.')
        return ConversationHandler.END

    text = update.message.text or '[без текста]'
    message = format_user_message(user, text)

    try:
        await context.bot.send_message(chat_id=ADMIN_ID, text=message)
        logger.info(f'Сообщение пользователя {user.id} отправлено менеджеру.')
    except Exception:
        logger.exception('Ошибка при отправке менеджеру:')
        await update.message.reply_text(
            '⚠️ Не удалось отправить сообщение менеджеру. Попробуйте позже.'
        )
        return ConversationHandler.END

    if is_within_working_hours():
        response = (
            '✅ Ваше сообщение отправлено.\n'
            'В ближайшее время Вам напишет наш менеджер.'
        )
    else:
        response = (
            '✅ Ваше сообщение отправлено.\n'
            'Наш менеджер свяжется с вами в рабочее время: '
            'с 10:00 до 19:00 по московскому времени.'
        )

    await update.message.reply_text(response)
    return ConversationHandler.END
