import pytest
from telegram.ext import Application, CommandHandler, ConversationHandler

from bot.handlers.registry import register_handlers
from bot.handlers.calculator import (
    CHOOSING_SIZE, CHOOSING_STYLE, CHOOSING_FACE_COUNT, CHOOSING_OPTIONS
)


def test_register_handlers_runs_without_error(app: Application) -> None:
    """
    Проверяет, что функция register_handlers не вызывает исключений.
    """
    try:
        register_handlers(app)
    except Exception as e:
        pytest.fail(f'register_handlers вызвал ошибку: {e}')


def test_handlers_registered(app: Application) -> None:
    """
    Проверяет, что после регистрации хендлеров они действительно добавлены.
    """
    register_handlers(app)
    assert len(app.handlers[0]) >= 4  # start + 3 FSM-хендлера


def test_contains_command_and_conversation_handlers(app: Application) -> None:
    """
    Проверяет, что среди зарегистрированных хендлеров есть
    CommandHandler и ConversationHandler.
    """
    register_handlers(app)
    types = {type(h) for h in app.handlers[0]}
    assert CommandHandler in types
    assert ConversationHandler in types


def test_calculator_conversation_states(app: Application) -> None:
    """
    Проверяет, что FSM калькулятора содержит нужные состояния.
    """
    register_handlers(app)
    calc_conv = next(
        (
            h for h in app.handlers[0]
            if isinstance(h, ConversationHandler)
            and any(ep.callback.__name__ == 'start_calculator' for ep in (
                h.entry_points
            ))
        ),
        None
    )
    assert calc_conv is not None
    assert CHOOSING_SIZE in calc_conv.states
    assert CHOOSING_STYLE in calc_conv.states
    assert CHOOSING_FACE_COUNT in calc_conv.states
    assert CHOOSING_OPTIONS in calc_conv.states
