def chunked(lst, n):
    # Разбивает список на подсписки по n элементов.
    return [lst[i:i + n] for i in range(0, len(lst), n)]
