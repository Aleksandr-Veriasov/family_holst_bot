from telegram.ext import ApplicationBuilder
from bot.config import TELEGRAM_TOKEN
from bot.handlers.registry import register_handlers
import logging
import sys


# Настройка логгирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)


def main():
    logger.info('Запуск бота...')
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    register_handlers(app)
    logger.info('Бот успешно запущен. Ожидаем команды.')
    app.run_polling()


if __name__ == '__main__':
    main()
