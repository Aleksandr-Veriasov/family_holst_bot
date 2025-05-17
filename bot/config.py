import os
from pathlib import Path

from dotenv import load_dotenv

# Загружаем переменные из .env
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# Получаем значения
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# Путь к базе данных
BASE_DIR = Path(__file__).resolve().parent.parent
IMAGE_DIR = BASE_DIR / 'data' / 'images'

# Проверка, если токен не найден — ошибка
if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_TOKEN не найден в .env файле.")
