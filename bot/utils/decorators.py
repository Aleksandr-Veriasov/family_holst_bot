from functools import wraps

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler


def ensure_message(handler_func):
    # Декоратор: проверяет наличие update.message перед вызовом хэндлера.
    @wraps(handler_func)
    async def wrapper(
        update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> int:
        if not update.message:
            return ConversationHandler.END
        return await handler_func(update, context)
    return wrapper
