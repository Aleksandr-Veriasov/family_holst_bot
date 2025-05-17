from bot.prices import BASE_PRICES, DRAWING_STYLES, EXTRA_OPTIONS


def calc_drawing_price(faces: int) -> int:
    # Расчёт стоимости отрисовки по числу лиц
    if faces <= 0:
        return 0
    return 1200 + (faces - 1) * 600


def calculate_total(data: dict) -> tuple[int, list[str]]:
    # Расчёт общей стоимости заказа
    size: str = data.get('size', '')
    style: str = data.get('style', '')
    faces: int = data.get('faces', 0)
    options: list[str] = data.get('options', [])

    total: int = 0
    lines: list[str] = []

    # Базовая цена
    base_price: int = BASE_PRICES.get(size, 0)
    total += base_price
    lines.append(f'• Размер: {size} — {base_price} ₽')

    # Отрисовка
    if style in DRAWING_STYLES:
        draw_price: int = calc_drawing_price(faces)
        total += draw_price
        lines.append(f'• Стиль: {style}')
        lines.append(f'• Лиц: {faces} — {draw_price} ₽')
    else:
        lines.append(f'• Стиль: {style}')

    # Доп. опции
    for opt in options:
        price: int = EXTRA_OPTIONS.get(opt, 0)
        total += price
        lines.append(f'• {opt} — {price} ₽')

    return total, lines


def format_summary(data: dict) -> str:
    # Форматирование итогового сообщения
    total, lines = calculate_total(data)
    return '🧾 Ваш заказ:\n' + '\n'.join(lines) + f'\n\n💰 Итого: {total} ₽'
