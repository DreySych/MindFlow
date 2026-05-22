def can_act(user):
    """Проверяет, авторизован ли пользователь и не заблокирован."""
    return user.is_authenticated and user.active
