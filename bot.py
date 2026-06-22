"""Основной модуль бота."""
import logging
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from config import Config
from database.db_manager import db_manager
from handlers import (
    handle_start, handle_next, handle_previous,
    handle_add_to_favorites, handle_add_to_blocked,
    handle_show_favorites, handle_show_blocked,
    handle_remove_from_favorites, handle_remove_from_blocked,
    handle_show_partners, handle_main_menu, handle_statistics,
    handle_settings, handle_change_age, handle_change_distance,
    handle_text_message, handle_admin_menu, handle_admin_users,
    handle_admin_stats, handle_admin_broadcast, send_message,
    handle_start_chat, handle_send_message, handle_exit_chat
)
from state_manager import state_manager

db_manager.initialize()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def run_bot():
    try:
        from vk_client import get_vk_session
        vk_session = get_vk_session()
        longpoll = VkBotLongPoll(vk_session, int(Config.GROUP_ID))
        logger.info("Бот запущен! Жду сообщение...")
        for event in longpoll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW:
                handle_message(event.obj.message)
    except Exception as e:
        logger.error(f"Ошибка бота: {e}")
        raise


def handle_message(message):
    user_id = message['from_id']
    text = message.get('text', '').lower().strip()
    logger.info(f"Сообщение от {user_id}: '{text}'")
    
    try:
        state = state_manager.get_state(user_id)
        
        # Выход из чата
        if text in ['выйти', 'выход', 'exit', 'стоп']:
            if state and state.get('mode') == 'in_chat':
                handle_exit_chat(user_id)
                return
        
        # Сообщения в чате
        if state and state.get('mode') == 'in_chat':
            if handle_send_message(user_id, text):
                return
        
        # Команда "чат N"
        if text.startswith('чат ') or text.startswith('chat '):
            try:
                match_num = int(text.split()[1])
                from data_storage import get_matches
                if 1 <= match_num <= len(get_matches(user_id)):
                    handle_start_chat(user_id, match_num)
                else:
                    send_message(user_id, "❌ Неверный номер мэтча")
            except:
                send_message(user_id, "❌ Используйте: чат 1")
            return
        
        # Ввод для настроек/рассылки
        if state and state.get('mode') in ['waiting_age', 'waiting_distance', 'waiting_broadcast']:
            if handle_text_message(user_id, text):
                return
        
        # Убираем эмодзи
        text_clean = text
        for emoji in ['🚫','❤️','🏠','🔍','📊','⚙️','🎉','🔐','👥','📢','❌','✅','📅','📍','💬']:
            text_clean = text_clean.replace(emoji, '')
        text_clean = text_clean.strip()
        
        # Роутинг с явными проверками
        if text_clean in ['начать', 'начать поиск', 'start', 'поиск'] or 'начать поиск' in text:
            handle_start(user_id)
        elif text_clean in ['следующий', 'далее', '>>', 'далее >>', 'след.', 'следующий >>'] or 'далее' in text:
            handle_next(user_id)
        elif text_clean in ['предыдущий', '<<', 'назад', 'пред.', '<< предыдущий', '<< назад'] or 'предыдущий' in text:
            handle_previous(user_id)
        elif text_clean in ['в избранное', 'лайк', 'добавить'] or ('в избранное' in text and 'список' not in text):
            handle_add_to_favorites(user_id)
        elif text_clean in ['в чёрный список', 'дизлайк', 'в чс', 'блок', 'чс'] or 'в чс' in text or 'чёрный список' in text:
            handle_add_to_blocked(user_id)
        elif text_clean in ['список избранных', 'избранное', 'favorites', 'избранные'] or 'избранное' in text:
            handle_show_favorites(user_id)
        elif text_clean in ['чёрный список', 'blocked', 'блок лист'] or 'чёрный список' in text:
            handle_show_blocked(user_id)
        elif text_clean in ['удалить из избранного', 'удалить', 'убрать'] or 'удалить' in text:
            handle_remove_from_favorites(user_id)
        elif text_clean in ['удалить из чёрного списка', 'разблокировать', 'разблок'] or 'разблокировать' in text:
            handle_remove_from_blocked(user_id)
        elif text_clean in ['список партнёров', 'партнёры', 'matches', 'мэтчи'] or 'мэтчи' in text:
            handle_show_partners(user_id)
        elif text_clean in ['статистика', 'stats', 'стата'] or 'статистика' in text:
            handle_statistics(user_id)
        elif text_clean in ['настройки', 'settings', 'параметры'] or 'настройки' in text:
            handle_settings(user_id)
        elif text_clean in ['изменить возраст', 'возраст'] or 'возраст' in text:
            handle_change_age(user_id)
        elif text_clean in ['изменить расстояние', 'расстояние'] or 'расстояние' in text:
            handle_change_distance(user_id)
        elif text_clean in ['админ', 'админка', 'admin', 'админ панель', 'админ-панель'] or 'админ' in text:
            handle_admin_menu(user_id)
        elif text_clean in ['пользователи', 'список пользователей', 'юзеры'] or 'пользователи' in text:
            handle_admin_users(user_id)
        elif text_clean in ['статистика пользователей'] or 'статистика пользователей' in text:
            handle_admin_stats(user_id)
        elif text_clean in ['рассылка', 'broadcast'] or 'рассылка' in text:
            handle_admin_broadcast(user_id)
        elif text_clean in ['главное меню', 'меню', 'главное', 'менюха'] or 'главное меню' in text:
            handle_main_menu(user_id)
        else:
            send_message(user_id, "Неизвестная команда. Используй кнопки меню 👇")
    except Exception as e:
        logger.error(f"Ошибка: {e}", exc_info=True)
        send_message(user_id, f"Произошла ошибка: {e}")


if __name__ == '__main__':
    run_bot()
