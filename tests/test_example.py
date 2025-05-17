from pathlib import Path
from typing import cast
from unittest.mock import AsyncMock, MagicMock, mock_open, patch

import pytest
from telegram import Message, Update
from telegram.ext import ContextTypes, ConversationHandler

from bot.handlers.examples import (
    CHOOSING_EXAMPLE_STYLE,
    send_example_images,
    show_example_styles,
)
from bot.keyboards.examples import style_keyboard
from bot.prices import STYLE_OPTIONS


@pytest.mark.asyncio
async def test_show_example_styles(
    fake_update: Update,
    fake_context: ContextTypes.DEFAULT_TYPE
) -> None:
    ''' Тест команды /examples. '''
    msg = cast(Message, fake_update.message)
    result = await show_example_styles(fake_update, fake_context)
    # Проверяем состояние
    assert result == CHOOSING_EXAMPLE_STYLE
    # Проверяем, что отправили сообщение
    reply = cast(AsyncMock, msg.reply_text)
    reply.assert_called_once()
    args, kwargs = reply.call_args
    assert 'посмотреть примеры' in args[0].lower()
    assert kwargs['reply_markup'] == style_keyboard


@pytest.mark.asyncio
async def test_send_example_images_valid(
    fake_update: Update,
    fake_context: ContextTypes.DEFAULT_TYPE
) -> None:
    ''' Тест отправки примеров. '''
    style = STYLE_OPTIONS[0]
    message = cast(Message, fake_update.message)
    message.text = style

    mock_images = [Path(f'img{i}.jpg') for i in range(1, 3)]

    with patch('bot.handlers.examples.IMAGE_DIR', Path('/fake/dir')), \
         patch('pathlib.Path.exists', return_value=True), \
         patch('pathlib.Path.iterdir', return_value=mock_images), \
         patch('builtins.open', mock_open(read_data=b'fake-image-bytes')), \
         patch('bot.handlers.examples.InputFile', return_value=MagicMock()):

        result = await send_example_images(fake_update, fake_context)

        assert result == ConversationHandler.END
        reply = cast(AsyncMock, message.reply_photo)
        assert reply.call_count >= 1
        assert reply.call_count == len(mock_images)


@pytest.mark.asyncio
async def test_send_example_images_no_style_folder(
    fake_update: Update,
    fake_context: ContextTypes.DEFAULT_TYPE
) -> None:
    ''' Тест отправки примеров, когда папка стиля не найдена. '''
    style = STYLE_OPTIONS[0]
    message = cast(Message, fake_update.message)
    message.text = style

    with patch('bot.handlers.examples.IMAGE_DIR', Path('/fake/dir')), \
         patch('pathlib.Path.exists', return_value=False):

        result = await send_example_images(fake_update, fake_context)

        assert result == ConversationHandler.END
        reply = cast(AsyncMock, message.reply_text)
        reply.assert_called_once()
        args, _ = reply.call_args
        assert 'папка' in args[0].lower() or 'не найдена' in args[0].lower()


@pytest.mark.asyncio
async def test_send_example_images_invalid_style(
    fake_update: Update,
    fake_context: ContextTypes.DEFAULT_TYPE
) -> None:
    ''' Тест отправки примеров, когда стиль не найден. '''
    message = cast(Message, fake_update.message)
    message.text = 'Неверный стиль'

    result = await send_example_images(fake_update, fake_context)
    assert result == CHOOSING_EXAMPLE_STYLE
    reply = cast(AsyncMock, message.reply_text)
    reply.assert_called_once()
    args, _ = reply.call_args
    assert 'выберите стиль' in args[0].lower()
