"""Модуль главного цикла бота VK-Tinder-Bot.

Этот модуль содержит основной цикл бота, который обрабатывает сообщения
от пользователей ВКонтакте через Bot LongPoll API. Он управляет
инициализацией базы данных, обработкой команд и graceful shutdown.

Пример:
    ```python
    # Запуск бота
    python bot.py
    ```
"""

import signal
from typing import Callable

from vk_api.bot_longpoll import VkBotEventType, VkBotLongPoll

from database.db_manager import db_manager
from .handlers import (
    handle_add_to_blocked,
    handle_add_to_favorites,
    handle_main_menu,
    handle_next,
    handle_previous,
    handle_remove_from_blocked,
    handle_remove_from_favorites,
    handle_search,
    handle_show_blocked,
    handle_show_favorites,
    handle_show_matches,
    handle_show_partners,
    handle_start,
)
from .vk_client import get_group_id, get_vk_session

# Словарь команд
COMMANDS: dict[tuple[str, ...], Callable] = {
    # Приветствие
    ("начать", "привет", "/start", "hi", "hello"): handle_start,
    # Поиск
    ("начать поиск",): handle_search,
    # Навигация
    ("следующий >>", "следующий"): handle_next,
    ("<< предыдущий", "предыдущий"): handle_previous,
    # Действия с партнёрами
    ("❤️ в избранное", "в избранное"): handle_add_to_favorites,
    ("🚫 в чёрный список", "в чёрный список"): handle_add_to_blocked,
    # Меню
    ("🏠 главное меню", "главное меню"): handle_main_menu,
    ("список партнёров",): handle_show_partners,
    ("список избранных",): handle_show_favorites,
    ("матчи",): handle_show_matches,
    ("чёрный список",): handle_show_blocked,
    # Удаление
    ("❌ удалить из избранного",): handle_remove_from_favorites,
    ("✅ удалить из чёрного списка",): handle_remove_from_blocked,
}


def _init_db() -> None:
    """Инициализирует базу данных, создаёт таблицы."""
    try:
        db_manager.initialize()
        db_manager.create_tables()
        print("✅ База данных инициализирована")
    except Exception as e:
        print(f"❌ Ошибка инициализации БД: {e}")
        print("Бот продолжит работу, но данные не будут сохраняться в БД")


def _extract_message(event) -> dict | None:
    """Извлекает данные сообщения из события LongPoll."""
    if event.type != VkBotEventType.MESSAGE_NEW:
        return None
    obj = getattr(event, "obj", None)
    if not obj:
        return None
    msg = obj.get("message")
    if not msg:
        return None
    if not msg.get("from_id") or not msg.get("text"):
        return None
    return msg


def _find_handler(text: str) -> Callable | None:
    """Находит обработчик команды по тексту сообщения."""
    for keywords, func in COMMANDS.items():
        for keyword in keywords:
            if text == keyword:
                return func
    return None


def _process_event(event) -> None:
    """Обрабатывает одно событие от LongPoll."""
    message = _extract_message(event)
    if message is None:
        return

    user_id = message["from_id"]
    text = message["text"].lower().strip()
    print(f"📨 Сообщение от {user_id}: '{text}'")

    handler = _find_handler(text)
    if handler:
        handler(user_id)
    else:
        print(f"⚠️ Неизвестная команда от {user_id}: '{text}'")


def _run_loop(longpoll) -> None:
    """Запускает основной цикл обработки событий."""
    shutdown = [False]  # мутатбельный контейнер для nonlocal

    def handle_shutdown(signum: int, frame) -> None:
        print("\n🛑 Остановка бота...")
        shutdown[0] = True

    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)

    for event in longpoll.listen():
        if shutdown[0]:
            break
        try:
            _process_event(event)
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            import traceback
            traceback.print_exc()


def run_bot() -> None:
    """Запускает основной цикл бота VK-Tinder-Bot."""
    print("⏳ Инициализация базы данных...")
    _init_db()

    session = get_vk_session()
    group_id = get_group_id(session)
    longpoll = VkBotLongPoll(session, group_id=group_id)

    print("🤖 Бот запущен! Жду сообщение...")
    print("💡 Напишите боту что-нибудь в ВК\n")

    _run_loop(longpoll)

    print("🔌 Закрытие подключений к БД...")
    db_manager.close()
    print("✅ Бот остановлен")
