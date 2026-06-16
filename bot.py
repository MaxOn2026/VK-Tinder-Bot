"""Модуль главного цикла бота."""
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_client import get_vk_session, get_group_id
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
    handle_unknown
)


# Словарь команд
COMMANDS = {
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
    ('чёрный список',): handle_show_blocked,
    
    # Удаление
    ('❌ удалить из избранного',): handle_remove_from_favorites,
    ('✅ удалить из чёрного списка',): handle_remove_from_blocked,
}


def run_bot():
    """Запускает бота."""
    session = get_vk_session()
    vk = session.get_api()
    group_id = get_group_id(session)
    
    longpoll = VkBotLongPoll(session, group_id=group_id)
    
    print("🤖 Бот запущен! Жду сообщение...")
    print("💡 Напишите боту что-нибудь в ВК\n")
    
    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            try:
                user_id = event.obj.message['from_id']
                text = event.obj.message['text'].lower().strip()
                
                print(f"📨 Сообщение от {user_id}: '{text}'")
                
                # Ищем подходящую команду
                handler = None
                for keywords, func in COMMANDS.items():
                    if text in keywords:
                        handler = func
                        break
                
                # Выполняем обработчик или unknown
                if handler:
                    handler(user_id)
                else:
                    handle_unknown(user_id)
                    
            except Exception as e:
                print(f"❌ Ошибка: {e}")
                import traceback
                traceback.print_exc()