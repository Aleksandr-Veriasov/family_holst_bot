import logging

from telegram import InputFile, Message, Update
from telegram.ext import ContextTypes, ConversationHandler

from bot.config import IMAGE_DIR
from bot.keyboards.common import main_menu_button
from bot.keyboards.examples import style_keyboard
from bot.prices import STYLE_OPTIONS
from bot.utils.decorators import ensure_message

logger = logging.getLogger(__name__)

CHOOSING_EXAMPLE_STYLE = 100  # уникальное состояние FSM


# Старт обработчика "Примеры работ"
@ensure_message
async def show_example_styles(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    assert update.message is not None
    message: Message = update.message

    await message.reply_text(
        '🎨 Выберите стиль, чтобы посмотреть примеры работ:',
        reply_markup=style_keyboard
    )
    return CHOOSING_EXAMPLE_STYLE


# Отправка примеров
@ensure_message
async def send_example_images(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    assert update.message is not None
    message: Message = update.message
    selected_style = message.text
    logger.info(f'[EXAMPLES] Пользователь выбрал стиль: {selected_style}')

    if selected_style not in STYLE_OPTIONS:
        await message.reply_text('Пожалуйста, выберите стиль из списка.')
        return CHOOSING_EXAMPLE_STYLE

    style_path = IMAGE_DIR / selected_style
    logger.info(f'[EXAMPLES] Путь к папке стиля: {style_path}')

    if not style_path.exists():
        logger.error(f'[EXAMPLES] Папка не найдена: {style_path}')
        await message.reply_text(
            f'❗️ Папка для стиля не найдена:\n{style_path}',
            reply_markup=main_menu_button
        )
        return ConversationHandler.END

    images = [f for f in style_path.iterdir() if f.suffix.lower() in (
        '.jpg', '.jpeg', '.png'
    )]
    images = images[:5]

    if not images:
        await message.reply_text(
            'Извините, пока нет примеров для этого стиля.',
            reply_markup=main_menu_button
        )
        return ConversationHandler.END

    await message.reply_text(f'🖼 Примеры работ в стиле «{selected_style}»:')
    for img_path in images:
        try:
            with open(img_path, 'rb') as file:
                await message.reply_photo(InputFile(file))
            logger.info(f'[EXAMPLES] Отправлено изображение: {img_path}')
        except Exception as e:
            logger.exception(f'[EXAMPLES] Ошибка при отправке {img_path}: {e}')
            await message.reply_text(
                f'⚠️ Не удалось отправить: {img_path.name}'
            )

    await message.reply_text(
        'Вы можете вернуться в главное меню:',
        reply_markup=main_menu_button
    )
    return ConversationHandler.END
