import pytest
from telegram import Update, User, Message, Chat
from telegram.ext import ContextTypes, Application
from typing import cast
from unittest.mock import AsyncMock, create_autospec, MagicMock


@pytest.fixture
def mock_user() -> User:
    return User(id=12345, is_bot=False, first_name="Test", username="testuser")


@pytest.fixture
def mock_chat() -> Chat:
    return Chat(id=12345, type="private")


@pytest.fixture
def fake_message(mock_user: User, mock_chat: Chat) -> Message:
    msg = create_autospec(Message, instance=True)
    msg.message_id = 1
    msg.text = "/start"
    msg.from_user = mock_user
    msg.chat = mock_chat
    msg.reply_text = AsyncMock()
    msg.reply_photo = AsyncMock()
    return msg


@pytest.fixture
def fake_update(fake_message: Message) -> Update:
    upd = create_autospec(Update, instance=True)
    upd.message = fake_message
    upd.effective_user = fake_message.from_user
    upd.effective_chat = fake_message.chat
    return upd


@pytest.fixture
def fake_context() -> ContextTypes.DEFAULT_TYPE:
    context = MagicMock()
    context.user_data = {}
    context.chat_data = {}
    context.bot = AsyncMock()
    return cast(ContextTypes.DEFAULT_TYPE, context)


@pytest.fixture
def app() -> Application:
    return Application.builder().token("fake-token").build()
