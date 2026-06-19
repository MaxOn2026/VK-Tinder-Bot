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
import sys

from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_client import get_vk_session, get_group_id
from database.db_manager import db_manager
from database.models.user import BotUser
from database.models.profile import VKProfile
from database.models.interaction import UserInteraction, MutualLike
from database.models.match import Match, Message
from database.models.interest import Interest
from database.models.location import Location
from handlers import (
    handle_start,
    handle_search,
    handle_next,
    handle_previous,
    handle_add_to_favorites,
    handle_add_to_blocked,
    handle_main_menu,
    handle_show_partners,
    handle_show_favorites,
    handle_show_blocked,
    handle_remove_from_favorites,
    handle_remove_from_blocked,
    handle_show_matches
)


# Словарь команд
COMMANDS: dict[tuple[str, ...], callable] = {
    # Приветствие
    ('начать', 'привет', '/start', 'hi', 'hello'): handle_start,
    
    # Поиск
    ('начать поиск',): handle_search,
    
    # Навигация
    ('следующий >>', 'следующий'): handle_next,
    ('<< предыдущий', 'предыдущий'): handle_previous,
    
    # Действия с партнёрами
    ('❤️ в избранное', 'в избранное'): handle_add_to_favorites,
    ('🚫 в чёрный список', 'в чёрный список'): handle_add_to_blocked,
    
    # Меню
    ('🏠 главное меню', 'главное меню'): handle_main_menu,
    ('список партнёров',): handle_show_partners,
    ('список избранных',): handle_show_favorites,
    ('матчи',): handle_show_matches,
    ('чёрный список',): handle_show_blocked,
    
    # Удаление
    ('❌ удалить из избранного',): handle_remove_from_favorites,
    ('✅ удалить из чёрного списка',): handle_remove_from_blocked,
}


def run_bot() -> None:
    """Запускает основной цикл бота VK-Tinder-Bot.
    
    Инициализирует базу данных, подключается к VK API через Bot LongPoll
    и начинает обработку входящих сообщений. Обрабатывает команды из
    словаря COMMANDS и управляет graceful shutdown через сигналы.
    
    Raises:
        Exception: При ошибке инициализации базы данных выводит предупреждение,
            но продолжает работу (без сохранения данных в БД).
    
    Пример:
        ```python
        # Запуск бота
        run_bot()
        ```
    """
    # Инициализация базы данных
    print("⏳ Инициализация базы данных...")
    try:
        db_manager.initialize()
        db_manager.create_tables()
        print("✅ База данных инициализирована")
    except Exception as e:
        print(f"❌ Ошибка инициализации БД: {e}")
        print("Бот продолжит работу, но данные не будут сохраняться в БД")

    session = get_vk_session()
    vk = session.get_api()
    group_id = get_group_id(session)
    
    longpoll = VkBotLongPoll(session, group_id=group_id)
    
    print("🤖 Бот запущен! Жду сообщение...")
    print("💡 Напишите боту что-нибудь в ВК\n")
    
    # Обработка graceful shutdown
    shutdown = False
    def handle_shutdown(signum: int, frame) -> None:
        """Обрабатывает сигналы завершения работы.
        
        Устанавливает флаг shutdown в True для корректного завершения
        основного цикла бота.
        
        Args:
            signum (int): Номер полученного сигнала.
            frame: Текущий фрейм стека (не используется).
        """
        nonlocal shutdown
        print("\n🛑 Остановка бота...")
        shutdown = True

    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)
    
    for event in longpoll.listen():
        if shutdown:
            break
            
        if event.type == VkBotEventType.MESSAGE_NEW:
            try:
                obj = event.obj
                if not obj or not obj.get('message'):
                    continue
                    
                message = obj['message']
                if not message.get('from_id') or not message.get('text'):
                    continue
                    
                user_id = message['from_id']
                text = message['text'].lower().strip()
                
                print(f"📨 Сообщение от {user_id}: '{text}'")
                
                # Ищем подходящую команду
                handler = None
                for keywords, func in COMMANDS.items():
                    if text in keywords:
                        handler = func
                        break
                
                # Выполняем обработчик или показываем подсказку
                if handler:
                    handler(user_id)
                else:
                    print(f"⚠️ Неизвестная команда от {user_id}: '{text}'")
                    
            except Exception as e:
                print(f"❌ Ошибка: {e}")
                import traceback
                traceback.print_exc()
    
    # Закрытие БД
    print("🔌 Закрытие подключений к БД...")
    db_manager.close()
    print("✅ Бот остановлен")