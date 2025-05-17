from datetime import datetime
from typing import cast
from unittest.mock import AsyncMock, patch

import pytest
import pytz
from telegram import Message, Update
from telegram.ext import ContextTypes, ConversationHandler

from bot.handlers.contact import (
    WAITING_FOR_MESSAGE,
    forward_to_manager,
    is_within_working_hours,
    request_contact,
)


@pytest.mark.asyncio
async def test_request_contact(
    fake_update: Update,
    fake_context: ContextTypes.DEFAULT_TYPE
) -> None:
    ''' Тест запроса контакта. '''
    message = cast(Message, fake_update.message)
    reply = cast(AsyncMock, message.reply_text)

    result = await request_contact(fake_update, fake_context)

    assert result == WAITING_FOR_MESSAGE
    reply.assert_called_once()

    args, _ = reply.call_args
    assert 'вопрос' in args[0].lower() or 'сообщение' in args[0].lower()


@pytest.mark.asyncio
async def test_forward_to_manager_during_work_hours(
    fake_update: Update,
    fake_context: ContextTypes.DEFAULT_TYPE
) -> None:
    ''' Тест пересылки сообщения менеджеру в рабочие часы. '''
    message = cast(Message, fake_update.message)
    message.text = 'Тестовое сообщение'

    with patch(
        'bot.handlers.contact.is_within_working_hours', return_value=True
    ):
        result = await forward_to_manager(fake_update, fake_context)

    assert result == ConversationHandler.END
    send_message = cast(AsyncMock, fake_context.bot.send_message)
    send_message.assert_called_once()
    reply = cast(AsyncMock, message.reply_text)
    reply.assert_called_once()
    args, _ = reply.call_args
    assert 'в ближайшее время' in args[0].lower()


@pytest.mark.asyncio
async def test_forward_to_manager_outside_work_hours(
    fake_update: Update,
    fake_context: ContextTypes.DEFAULT_TYPE
) -> None:
    ''' Тест пересылки сообщения менеджеру вне рабочего времени. '''
    message = cast(Message, fake_update.message)
    message.text = 'Сообщение вне времени'

    with patch(
        'bot.handlers.contact.is_within_working_hours', return_value=False
    ):
        result = await forward_to_manager(fake_update, fake_context)

    assert result == ConversationHandler.END
    send_message = cast(AsyncMock, fake_context.bot.send_message)
    send_message.assert_called_once()
    reply = cast(AsyncMock, message.reply_text)
    reply.assert_called_once()
    args, _ = reply.call_args
    assert 'рабочее время' in args[0].lower()


@pytest.mark.asyncio
async def test_forward_to_manager_failure(
    fake_update: Update,
    fake_context: ContextTypes.DEFAULT_TYPE
) -> None:
    ''' Тест пересылки сообщения менеджеру с ошибкой. '''
    message = cast(Message, fake_update.message)
    message.text = 'Ошибка'
    send_message = cast(AsyncMock, fake_context.bot.send_message)
    send_message.side_effect = Exception('Ошибка отправки')

    result = await forward_to_manager(fake_update, fake_context)

    assert result == ConversationHandler.END
    reply = cast(AsyncMock, message.reply_text)
    reply.assert_called_once()
    args, _ = reply.call_args
    assert 'не удалось' in args[0].lower()


@pytest.mark.parametrize(
    'mock_time,expected',
    [
        (datetime(2024, 1, 1, 10, 0), True),   # 10:00 — в рабочее
        (datetime(2024, 1, 1, 18, 59), True),  # 18:59 — в рабочее
        (datetime(2024, 1, 1, 9, 59), False),  # 9:59 — до начала
        (datetime(2024, 1, 1, 19, 0), False),  # 19:00 — вне рабочего
    ]
)
def test_is_within_working_hours(mock_time: datetime, expected: bool) -> None:
    ''' Тест функции is_within_working_hours. '''
    moscow_tz = pytz.timezone('Europe/Moscow')
    localized_time = moscow_tz.localize(mock_time)

    with patch('bot.handlers.contact.datetime') as mock_datetime:
        mock_datetime.now.return_value = localized_time
        mock_datetime.time = datetime.time
        result = is_within_working_hours()
        assert result == expected
