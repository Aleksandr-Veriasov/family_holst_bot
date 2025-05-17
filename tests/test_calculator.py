import pytest
from bot.utils.calculator import calculate_total, format_summary
from telegram import Update, Message
from telegram.ext import ContextTypes, ConversationHandler
from typing import cast
from unittest.mock import AsyncMock
from bot.states import (
    CHOOSING_SIZE,
    CHOOSING_STYLE,
    CHOOSING_FACE_COUNT,
    CHOOSING_OPTIONS,
)

from bot.handlers.calculator import (
    start_calculator,
    size_chosen,
    style_chosen,
    face_count_chosen,
    options_chosen,
)
from bot.keyboards.calculator import (
    size_keyboard, style_keyboard, option_keyboard
)


@pytest.mark.parametrize(
    'order, expected_total, expected_in_lines',
    [
        # 1. Только базовая цена
        (
            {
                'size': '30×40',
                'style': 'Просто фото на холсте',
                'faces': 0,
                'options': []
            },
            1545,
            ['Размер: 30×40', 'Стиль: Просто фото на холсте']
        ),

        # 2. Стиль с 1 лицом (Dream Art)
        (
            {'size': '30×40', 'style': 'Dream Art', 'faces': 1, 'options': []},
            1545 + 1200,
            ['Стиль: Dream Art', 'Лиц: 1 — 1200 ₽']
        ),

        # 3. Стиль с 3 лицами (Dream Art)
        (
            {'size': '30×40', 'style': 'Dream Art', 'faces': 3, 'options': []},
            1545 + 1200 + 600 * 2,
            ['Лиц: 3 — 2400 ₽']
        ),

        # 4. Стиль с 1 лицом + 2 опции
        (
            {
                'size': '40×60',
                'style': 'Digital Art',
                'faces': 1,
                'options': ['Подарочная упаковка', 'Фактурный гель']
            },
            2085 + 1200 + 245 + 350,
            ['Фактурный гель — 350 ₽', 'Подарочная упаковка — 245 ₽']
        ),

        # 5. Неизвестные значения
        (
            {
                'size': '100×100',
                'style': 'Стиль которого нет',
                'faces': 2,
                'options': ['Несуществующее']
            },
            0,
            []
        ),
    ]
)
def test_calculate_total_cases(
    order: dict, expected_total: int, expected_in_lines: list[str]
) -> None:
    """
    Тестирует функцию calculate_total на различных входных данных.
    :param order: Входной заказ (словарь с параметрами)
    :param expected_total: Ожидаемая итоговая стоимость
    :param expected_in_lines: Ожидаемые строки в результатах
    """
    total, lines = calculate_total(order)
    assert total == expected_total  # Проверка итоговой стоимости
    for expected in expected_in_lines:
        # Проверка наличия ожидаемых строк в результатах
        assert any(expected in line for line in lines)


@pytest.mark.parametrize(
    'order, expected_substrings',
    [
        # Простой случай
        (
            {
                'size': '30×40',
                'style': 'Просто фото на холсте',
                'faces': 0,
                'options': []
            },
            ['Размер: 30×40', 'Стиль: Просто фото на холсте', '💰 Итого:']
        ),
        # Стиль с лицами
        (
            {
                'size': '40×60',
                'style': 'Digital Art',
                'faces': 2,
                'options': []
            },
            ['Стиль: Digital Art', 'Лиц: 2 — 1800 ₽', '💰 Итого:']
        ),
        # Стиль + опции
        (
            {
                'size': '50×70',
                'style': 'Dream Art',
                'faces': 1,
                'options': ['Фактурный гель']
            },
            [
                'Размер: 50×70',
                'Лиц: 1 — 1200 ₽',
                'Фактурный гель — 350 ₽',
                '💰 Итого:'
            ]
        ),
        # Пустой / невалидный заказ
        (
            {
                'size': 'UNKNOWN',
                'style': '???',
                'faces': 0,
                'options': ['Что-то странное']
            },
            ['💰 Итого:']
        )
    ]
)
def test_format_summary_variants(
    order: dict, expected_substrings: list[str]
) -> None:
    '''
    Тестирует функцию format_summary на различных входных данных.
    :param order: Входной заказ (словарь с параметрами)
    :param expected_substrings: Ожидаемые подстроки в итоговом формате
    '''
    result = format_summary(order)

    assert isinstance(result, str)  # Проверка, что результат — строка
    for substr in expected_substrings:
        assert substr in result  # Проверка наличия подстрок в результате


@pytest.mark.asyncio
async def test_style_chosen_simple_style(
    fake_update: Update, fake_context: ContextTypes.DEFAULT_TYPE
) -> None:
    ''' Тестируем корректный выбор стиля. '''
    message = cast(Message, fake_update.message)
    message.text = 'Просто фото на холсте'
    result = await style_chosen(fake_update, fake_context)
    assert result == CHOOSING_OPTIONS

    user_data = cast(dict, fake_context.user_data)
    assert user_data['style'] == 'Просто фото на холсте'

    reply = cast(AsyncMock, message.reply_text)
    reply.assert_called_once()
    args, kwargs = reply.call_args
    assert 'стиль выбран' in args[0].lower()
    assert kwargs['reply_markup'] == option_keyboard


@pytest.mark.asyncio
async def test_style_chosen_with_faces(
    fake_update: Update, fake_context: ContextTypes.DEFAULT_TYPE
) -> None:
    ''' Тестируем выбор стиля с лицами. '''
    message = cast(Message, fake_update.message)
    message.text = 'Dream Art'
    result = await style_chosen(fake_update, fake_context)
    assert result == CHOOSING_FACE_COUNT

    user_data = cast(dict, fake_context.user_data)
    assert user_data['style'] == 'Dream Art'

    reply = cast(AsyncMock, message.reply_text)
    reply.assert_called_once()
    args, _ = reply.call_args
    assert 'сколько лиц' in args[0].lower()


@pytest.mark.asyncio
async def test_style_chosen_invalid(
    fake_update: Update, fake_context: ContextTypes.DEFAULT_TYPE
) -> None:
    ''' Тестируем некорректный выбор стиля. '''
    message = cast(Message, fake_update.message)
    message.text = 'Случайный стиль'
    result = await style_chosen(fake_update, fake_context)

    assert result == CHOOSING_STYLE
    reply = cast(AsyncMock, message.reply_text)
    reply.assert_called_once_with('Пожалуйста, выберите стиль из списка.')


@pytest.mark.asyncio
async def test_size_chosen_valid(
    fake_update: Update, fake_context: ContextTypes.DEFAULT_TYPE
) -> None:
    ''' Тестируем корректный выбор размера холста. '''
    message = cast(Message, fake_update.message)
    message.text = '30×40'
    result = await size_chosen(fake_update, fake_context)
    assert result == CHOOSING_STYLE
    user_data = cast(dict, fake_context.user_data)
    assert user_data['size'] == '30×40'
    reply = cast(AsyncMock, message.reply_text)
    reply.assert_called_once()
    args, kwargs = reply.call_args
    assert 'стиль портрета' in args[0].lower()
    assert kwargs['reply_markup'].keyboard == style_keyboard.keyboard


@pytest.mark.asyncio
async def test_size_chosen_invalid(
    fake_update: Update, fake_context: ContextTypes.DEFAULT_TYPE
) -> None:
    ''' Тестируем некорректный выбор размера холста. '''
    message = cast(Message, fake_update.message)
    message.text = '150×150'  # Недопустимый размер
    result = await size_chosen(fake_update, fake_context)

    assert result == CHOOSING_SIZE
    reply = cast(AsyncMock, message.reply_text)
    reply.assert_called_once_with(
        'Пожалуйста, выберите размер из предложенных.'
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'input_text, expected_state, expected_faces, should_call_keyboard',
    [
        ('1', CHOOSING_OPTIONS, 1, True),
        ('5', CHOOSING_OPTIONS, 5, True),
        ('10', CHOOSING_OPTIONS, 10, True),
        ('0', CHOOSING_FACE_COUNT, None, False),
        ('11', CHOOSING_FACE_COUNT, None, False),
        ('abc', CHOOSING_FACE_COUNT, None, False),
        ('', CHOOSING_FACE_COUNT, None, False),
    ]
)
async def test_face_count_chosen_param(
    input_text: str,
    expected_state: int,
    expected_faces: int | None,
    should_call_keyboard: bool,
    fake_update: Update,
    fake_context: ContextTypes.DEFAULT_TYPE
) -> None:
    '''
    Тестируем выбор количества лиц.
    :param input_text: Ввод пользователя.
    :param expected_state: Ожидаемое состояние после обработки.
    :param expected_faces: Ожидаемое количество лиц.
    :param should_call_keyboard: Должен ли вызываться клавиатура.
    '''
    assert fake_update.message is not None
    msg = cast(Message, fake_update.message)
    msg.text = input_text

    result = await face_count_chosen(fake_update, fake_context)

    assert result == expected_state
    user_data = cast(dict, fake_context.user_data)
    if expected_faces is not None:
        assert user_data['faces'] == expected_faces
    else:
        assert 'faces' not in user_data

    reply = cast(AsyncMock, msg.reply_text)
    reply.assert_called_once()
    args, kwargs = reply.call_args

    if should_call_keyboard:
        assert 'дополнительно' in args[0].lower()
        assert kwargs['reply_markup'] == option_keyboard
    else:
        assert 'введите число' in args[0].lower()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'input_text, '
    'expected_state, '
    'initial_options, '
    'expected_options, '
    'summary_called, '
    'expected_reply',
    [
        # Новый выбор опции
        (
            'Подарочная упаковка',
            CHOOSING_OPTIONS,
            [],
            ['Подарочная упаковка'],
            False,
            'добавлено'
        ),
        # Повторный выбор той же опции
        (
            'Подарочная упаковка',
            CHOOSING_OPTIONS,
            ['Подарочная упаковка'],
            ['Подарочная упаковка'],
            False,
            'уже выбрана'
        ),
        # Неизвестная опция
        (
            'Неизвестная опция',
            CHOOSING_OPTIONS,
            [],
            [],
            False,
            'Пожалуйста, выберите одну из доступных опций'
        ),
        # Завершение выбора
        (
            'Готово',
            ConversationHandler.END,
            ['Подарочная упаковка'],
            ['Подарочная упаковка'],
            True,
            'завершён'
        )
    ]
)
async def test_options_chosen_param(
    input_text: str,
    expected_state: int,
    initial_options: list[str],
    expected_options: list[str],
    summary_called: bool,
    expected_reply: str,
    fake_update: Update,
    fake_context: ContextTypes.DEFAULT_TYPE,
    monkeypatch
) -> None:
    '''
    Тестируем выбор дополнительных опций.
    :param input_text: Ввод пользователя.
    :param expected_state: Ожидаемое состояние после обработки.
    :param initial_options: Начальные опции.
    :param expected_options: Ожидаемые опции после обработки.
    :param summary_called: Должен ли быть вызван summarize_order.
    :param expected_reply: Ожидаемый текст ответа.
    '''
    msg = cast(Message, fake_update.message)
    msg.text = input_text
    user_data = cast(dict, fake_context.user_data)
    user_data['options'] = initial_options.copy()

    # Подменяем summarize_order если "Готово"
    summarize_mock = AsyncMock()
    monkeypatch.setattr(
        'bot.handlers.calculator.summarize_order', summarize_mock
    )

    result = await options_chosen(fake_update, fake_context)

    assert result == expected_state
    assert user_data['options'] == expected_options

    msg_reply = cast(AsyncMock, msg.reply_text)
    msg_reply.assert_called_once()
    args, kwarg = msg_reply.call_args
    assert expected_reply.lower() in args[0].lower()

    if summary_called:
        summarize_mock.assert_awaited_once_with(fake_update, fake_context)
    else:
        summarize_mock.assert_not_called()


@pytest.mark.asyncio
async def test_start_calculator_sends_keyboard(
    fake_update: Update, fake_context: ContextTypes.DEFAULT_TYPE
) -> None:
    ''' Тестируем отправку клавиатуры при старте калькулятора '''
    result = await start_calculator(fake_update, fake_context)
    message = cast(Message, fake_update.message)
    reply = cast(AsyncMock, message.reply_text)
    reply.assert_called_once()

    # Проверим текст и клавиатуру
    args, kwargs = reply.call_args
    assert 'размер холста' in args[0].lower()
    assert kwargs['reply_markup'].keyboard == size_keyboard.keyboard

    # Проверим возврат состояния
    assert result == CHOOSING_SIZE
