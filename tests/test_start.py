from typing import cast
from unittest.mock import AsyncMock

import pytest
from telegram import Message, Update
from telegram.ext import ContextTypes

from bot.handlers.start import start_command
from bot.keyboards.main_menu import main_menu


@pytest.mark.asyncio
async def test_start_command(
    fake_update: Update,
    fake_context: ContextTypes.DEFAULT_TYPE
) -> None:
    ''' Тестирование команды /start '''
    message = cast(Message, fake_update.message)

    # Запуск команды
    await start_command(fake_update, fake_context)

    reply = cast(AsyncMock, message.reply_text)
    reply.assert_called_once()

    args, kwargs = reply.call_args
    assert 'оформить заказ' in args[0].lower()
    assert kwargs['reply_markup'] == main_menu
