from django.core.mail import send_mail
from django.conf import settings


def send_recovery_code(email, code):
    """Отправка кода восстановления на почту"""
    subject = 'MindFlow - Код восстановления пароля'
    message = f'''
    Здравствуйте!

    Вы запросили восстановление пароля для аккаунта MindFlow.

    Ваш код восстановления: {code}

    Код действителен в течение 10 минут.

    Если вы не запрашивали восстановление пароля, просто проигнорируйте это письмо.

    С уважением,
    Команда MindFlow
    '''

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [email],
        fail_silently=False,
    )
