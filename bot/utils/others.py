def is_valid_email(email):
    # Шаблон для проверки валидности email
    import re
    pattern = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')

    # Проверка соответствия шаблону
    return bool(pattern.match(email))