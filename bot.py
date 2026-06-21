"""Основной модуль бота."""
import logging
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.utils import get_random_id
from config import Config
from database.db_manager import db_manager
from handlers import (
    handle_start,
    handle_next,
    handle_previous,
    handle_add_to_favorites,
    handle_add_to_blocked,
    handle_show_favorites,
    handle_show_blocked,
    handle_remove_from_favorites,
    handle_remove_from_blocked,
    handle_show_partners,
    handle_main_menu,
    handle_statistics,
    handle_settings,
    handle_change_age,
    handle_change_distance,
    handle_text_message,
    send_message
)

# Инициализация базы данных
db_manager.initialize()

# Логирование
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_bot():
    """Запускает бота."""
    try:
        vk_session = get_vk_session()
        longpoll = VkBotLongPoll(vk_session, int(Config.GROUP_ID))
        
        logger.info("🤖 Бот запущен! Жду сообщение...")
        logger.info("💡 Напишите боту что-нибудь в ВК")
        
        for event in longpoll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW:
                message = event.obj.message
                handle_message(message)
                
    except Exception as e:
        logger.error(f"❌ Ошибка бота: {e}")
        raise


def get_vk_session():
    """Получает сессию VK API."""
    from vk_client import get_vk_session as _get_session
    return _get_session()


def handle_message(message):
    """Обрабатывает входящее сообщение."""
    user_id = message['from_id']
    text = message['text'].lower().strip()
    
    logger.info(f"📨 Сообщение от {user_id}: '{text}'")
    
    try:
        # Сначала проверяем, не ожидает ли бот ввода от пользователя
        from state_manager import state_manager
        state = state_manager.get_state(user_id)
        
        if state and state.get('mode') in ['waiting_age', 'waiting_distance']:
            logger.info(f"→ Обработка текстового ввода от {user_id}")
            if handle_text_message(user_id, text):
                return
        
        # Роутинг команд
        if text in ['начать', 'начать поиск', 'start']:
            logger.info(f"→ Вызван handle_start для {user_id}")
            handle_start(user_id)
        elif text in ['следующий', 'далее', '>>', 'следующий >>']:
            logger.info(f"→ Вызван handle_next для {user_id}")
            handle_next(user_id)
        elif text in ['предыдущий', '<<', '<< предыдущий']:
            logger.info(f"→ Вызван handle_previous для {user_id}")
            handle_previous(user_id)
        elif text in ['в избранное', '❤️', 'лайк', '❤️ в избранное']:
            logger.info(f"→ Вызван handle_add_to_favorites для {user_id}")
            handle_add_to_favorites(user_id)
        elif text in ['в чёрный список', '🚫', 'дизлайк', '🚫 в чёрный список']:
            logger.info(f"→ Вызван handle_add_to_blocked для {user_id}")
            handle_add_to_blocked(user_id)
        elif text in ['список избранных', 'избранное', 'favorites']:
            logger.info(f"→ Вызван handle_show_favorites для {user_id}")
            handle_show_favorites(user_id)
        elif text in ['чёрный список', 'blocked']:
            logger.info(f"→ Вызван handle_show_blocked для {user_id}")
            handle_show_blocked(user_id)
        elif text in ['удалить из избранного', '❌', '❌ удалить из избранного']:
            logger.info(f"→ Вызван handle_remove_from_favorites для {user_id}")
            handle_remove_from_favorites(user_id)
        elif text in ['удалить из чёрного списка', '✅', '✅ удалить из чёрного списка']:
            logger.info(f"→ Вызван handle_remove_from_blocked для {user_id}")
            handle_remove_from_blocked(user_id)
        elif text in ['список партнёров', 'партнёры', 'matches']:
            logger.info(f"→ Вызван handle_show_partners для {user_id}")
            handle_show_partners(user_id)
        elif text in ['статистика', '📊 статистика', 'stats']:
            logger.info(f"→ Вызван handle_statistics для {user_id}")
            handle_statistics(user_id)
        elif text in ['настройки', '⚙️ настройки', 'settings']:
            logger.info(f"→ Вызван handle_settings для {user_id}")
            handle_settings(user_id)
        elif text in ['изменить возраст', '📅 изменить возраст', 'возраст']:
            logger.info(f"→ Вызван handle_change_age для {user_id}")
            handle_change_age(user_id)
        elif text in ['изменить расстояние', '📍 изменить расстояние', 'расстояние']:
            logger.info(f"→ Вызван handle_change_distance для {user_id}")
            handle_change_distance(user_id)
        elif text in ['главное меню', 'меню', '🏠', '🏠 главное меню', 'главное']:
            logger.info(f"→ Вызван handle_main_menu для {user_id}")
            handle_main_menu(user_id)
        else:
            logger.warning(f"⚠️ Неизвестная команда: '{text}'")
            send_message(user_id, "❓ Неизвестная команда. Используйте кнопки или напишите 'начать'")
    except Exception as e:
        logger.error(f"❌ Ошибка обработки команды '{text}': {e}", exc_info=True)
        send_message(user_id, f"❌ Произошла ошибка: {e}")


if __name__ == '__main__':
    run_bot()