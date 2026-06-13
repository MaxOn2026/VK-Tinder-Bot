"""Модуль обработчиков команд бота."""
import random
from vk_client import get_vk_session
from keyboards import create_main_keyboard


def send_message(user_id, message, attachment=None, keyboard=None):
    """Отправляет сообщение пользователю."""
    vk = get_vk_session().get_api()
    params = {
        'user_id': user_id,
        'message': message,
        'random_id': random.randint(-2147483648, 2147483647)
    }
    if attachment:
        params['attachment'] = attachment
    if keyboard:
        params['keyboard'] = keyboard
    
    vk.messages.send(**params)


def handle_start(user_id):
    """Обработка приветствия."""
    print(f"  → Отправляю приветствие пользователю {user_id}")
    send_message(
        user_id,
        "Привет! Я VKinder Bot. Найду тебе пару! 👇",
        keyboard=create_main_keyboard()
    )


def handle_search(user_id):
    """Обработка 'Начать поиск'."""
    # TODO: здесь будет реальный поиск людей через VK API
    send_message(user_id, "🔍 Ищу подходящую пару...")


def handle_next(user_id):
    """Обработка 'Дальше'."""
    # TODO: показать следующего кандидата
    send_message(user_id, "➡️ Показываю следующего...")


def handle_favorite(user_id):
    """Обработка 'В избранное'."""
    # TODO: запись в БД (отвечает напарник)
    send_message(user_id, "❤️ Добавлено в избранное!")


def handle_unknown(user_id):
    """Обработка неизвестной команды."""
    print("  → Неизвестная команда")
    send_message(
        user_id,
        "Я не понял. Вот что я умею:",
        keyboard=create_main_keyboard()
    )