"""Модуль главного цикла бота."""
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_client import get_vk_session, get_group_id
from handlers import (
    handle_start,
    handle_search,
    handle_next,
    handle_favorite,
    handle_unknown
)


# Словарь команд
COMMANDS = {
    ('начать', 'привет', '/start', 'hi', 'hello'): handle_start,
    ('начать поиск',): handle_search,
    ('дальше',): handle_next,
    ('в избранное',): handle_favorite,
}


def run_bot():
    """Запускает бота."""
    session = get_vk_session()
    vk = session.get_api()
    group_id = get_group_id(session)
    
    longpoll = VkBotLongPoll(session, group_id=group_id)
    
    print("🤖 Бот запущен! Жду сообщения...")
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