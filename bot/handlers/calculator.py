import logging
from typing import cast

from telegram import Message, ReplyKeyboardRemove, Update
from telegram.ext import ContextTypes, ConversationHandler

from bot.keyboards.calculator import (
    option_keyboard, size_keyboard, style_keyboard
)
from bot.prices import AVAILABLE_SIZES, EXTRA_OPTIONS, STYLE_OPTIONS
from bot.states import (
    CHOOSING_FACE_COUNT,
    CHOOSING_OPTIONS,
    CHOOSING_SIZE,
    CHOOSING_STYLE,
)
from bot.utils.calculator import format_summary
from bot.utils.decorators import ensure_message

logger = logging.getLogger(__name__)


@ensure_message
async def start_calculator(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    # Запуск калькулятора.
    assert update.message is not None
    message: Message = update.message

    await message.reply_text(
        '📐 Выберите размер холста:',
        reply_markup=size_keyboard
    )
    return CHOOSING_SIZE


@ensure_message
async def size_chosen(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    # Обработчик выбора размера.
    assert update.message is not None
    message: Message = update.message
    size = message.text

    if size not in AVAILABLE_SIZES:
        await message.reply_text(
            'Пожалуйста, выберите размер из предложенных.'
        )
        return CHOOSING_SIZE

    user_data = cast(dict, context.user_data)
    user_data['size'] = size
    logger.info(f'Пользователь выбрал размер: {size}')

    await message.reply_text(
        f'✅ Выбран размер - {size}.\n Какой стиль портрета Вас интересует:',
        reply_markup=style_keyboard
    )
    return CHOOSING_STYLE


@ensure_message
async def style_chosen(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    # Обработчик выбора стиля.
    assert update.message is not None
    message: Message = update.message
    style = message.text

    if style not in STYLE_OPTIONS:
        await message.reply_text(
            'Пожалуйста, выберите стиль из списка.'
        )
        return CHOOSING_STYLE

    user_data = cast(dict, context.user_data)
    user_data['style'] = style
    logger.info(f'Выбран стиль: {style}')

    if style != 'Просто фото на холсте':
        await message.reply_text(
            '👤 Сколько лиц будет на портрете?\n'
            '(Пожалуйста, введите число от 1 до 10.)'
        )
        return CHOOSING_FACE_COUNT
    else:
        user_data = cast(dict, context.user_data)
        user_data['faces'] = 0
        await message.reply_text(
            '✅ Стиль выбран.\n\nВам потребуется что-то дополнительно?'
            '\nКогда закончите выбор, нажмите "Готово".',
            reply_markup=option_keyboard
        )
        return CHOOSING_OPTIONS


@ensure_message
async def face_count_chosen(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    # Обработчик выбора количества лиц.
    assert update.message is not None
    message: Message = update.message
    text = message.text or ''

    try:
        count = int(text)
        if count < 1 or count > 10:
            raise ValueError
    except ValueError:
        await message.reply_text(
            'Пожалуйста, введите число от 1 до 10.'
        )
        return CHOOSING_FACE_COUNT

    user_data = cast(dict, context.user_data)
    user_data['faces'] = count
    logger.info(f'Выбрано лиц: {count}')

    await message.reply_text(
        '✅ Кол-во лиц сохранено.\n\nВам потребуется что-то дополнительно?'
        '\nКогда закончите выбор, нажмите "Готово".',
        reply_markup=option_keyboard
    )
    return CHOOSING_OPTIONS


@ensure_message
async def options_chosen(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    # Обработчик выбора дополнительных опций.
    assert update.message is not None
    message: Message = update.message
    selected = message.text or ''
    user_data = cast(dict, context.user_data)

    if selected == 'Готово':
        user_data.setdefault('options', [])
        logger.info(f'Итоговые данные: {context.user_data}')
        await message.reply_text(
            '✅ Выбор опций завершён.',
            reply_markup=ReplyKeyboardRemove()
        )
        await summarize_order(update, context)  # сразу расчёт
        return ConversationHandler.END

    if selected not in EXTRA_OPTIONS:
        await message.reply_text(
            'Пожалуйста, выберите одну из доступных опций или '
            'нажмите "Готово".'
        )
        return CHOOSING_OPTIONS

    user_data.setdefault('options', [])

    if selected not in user_data['options']:
        user_data['options'].append(selected)
        logger.info(f'Добавлена опция: {selected}')
        await message.reply_text(f'Добавлено: {selected}')
    else:
        await message.reply_text('Эта опция уже выбрана.')

    return CHOOSING_OPTIONS


@ensure_message
async def summarize_order(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    assert update.message is not None
    message: Message = update.message
    user_data = cast(dict, context.user_data)

    await message.reply_text(format_summary(user_data))
    return ConversationHandler.END
