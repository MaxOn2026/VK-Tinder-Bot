"""Основной модуль бота."""

import logging
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from config import Config

# 1. СНАЧАЛА инициализируем БД
from database.db_manager import db_manager

db_manager.initialize()

# 2. ПОТОМ импортируем handlers
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
    handle_admin_menu,
    handle_admin_users,
    handle_admin_stats,
    handle_admin_broadcast,
    send_message,
    handle_start_chat,
    handle_send_message,
    handle_exit_chat,
)
from state_manager import state_manager

# Настройка логирования
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Словарь команд для упрощения роутинга
COMMAND_ROUTES = {
    'начать': handle_start,
    'начать поиск': handle_start,  # ← ДОБАВИТЬ
    'start': handle_start,
    'поиск': handle_start,
    
    'следующий': handle_next,
    'следующий >>': handle_next,  # ← ДОБАВИТЬ
    'далее': handle_next,
    'далее >>': handle_next,  # ← ДОБАВИТЬ
    '>>': handle_next,
    
    'предыдущий': handle_previous,
    '<< предыдущий': handle_previous,  # ← ДОБАВИТЬ
    '<< назад': handle_previous,  # ← ДОБАВИТЬ
    'назад': handle_previous,
    '<<': handle_previous,
    
    'в избранное': handle_add_to_favorites,
    'лайк': handle_add_to_favorites,
    'добавить': handle_add_to_favorites,
    
    'в чс': handle_add_to_blocked,
    'в чёрный список': handle_add_to_blocked,  # ← ДОБАВИТЬ
    'чс': handle_add_to_blocked,
    'блок': handle_add_to_blocked,
    
    'избранное': handle_show_favorites,
    'список избранных': handle_show_favorites,  # ← ДОБАВИТЬ
    
    'чёрный список': handle_show_blocked,
    
    'удалить': handle_remove_from_favorites,
    'удалить из избранного': handle_remove_from_favorites,  # ← ДОБАВИТЬ
    'разблокировать': handle_remove_from_blocked,
    'удалить из чёрного списка': handle_remove_from_blocked,  # ← ДОБАВИТЬ
    
    'мэтчи': handle_show_partners,
    'партнёры': handle_show_partners,
    'список партнёров': handle_show_partners,  # ← ДОБАВИТЬ
    
    'статистика': handle_statistics,
    'настройки': handle_settings,
    'возраст': handle_change_age,
    'изменить возраст': handle_change_age,  # ← ДОБАВИТЬ
    'расстояние': handle_change_distance,
    'изменить расстояние': handle_change_distance,  # ← ДОБАВИТЬ
    
    'админ': handle_admin_menu,
    'админка': handle_admin_menu,  # ← ДОБАВИТЬ
    'админ панель': handle_admin_menu,  # ← ДОБАВИТЬ
    'админ-панель': handle_admin_menu,
    'пользователи': handle_admin_users,
    'статистика пользователей': handle_admin_stats,
    'рассылка': handle_admin_broadcast,
    
    'меню': handle_main_menu,
    'главное меню': handle_main_menu,
}

def run_bot():
    """Запуск бота."""
    # Проверяем конфигурацию
    if not Config.GROUP_ID:
        logger.error("GROUP_ID не задан в .env файле!")
        raise ValueError("Отсутствует переменная GROUP_ID в конфигурации")

    try:
        from vk_client import get_vk_session

        vk_session = get_vk_session()
        longpoll = VkBotLongPoll(vk_session, int(Config.GROUP_ID))
        logger.info(f"Бот запущен для группы {Config.GROUP_ID}. Жду сообщения...")

        for event in longpoll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW:
                handle_message(event.obj.message)

    except Exception as e:
        logger.error(f"Ошибка бота: {e}", exc_info=True)
        raise


def handle_message(message):
    """Обработка входящего сообщения."""
    user_id = message["from_id"]
    text = message.get("text", "").lower().strip()
    logger.info(f"Сообщение от {user_id}: '{text}'")

    try:
        state = state_manager.get_state(user_id)

        # Выход из чата
        if text in ["выйти", "выход", "exit", "стоп"]:
            if state and state.get("mode") == "in_chat":
                handle_exit_chat(user_id)
                return

        # Сообщения в чате
        if state and state.get("mode") == "in_chat":
            if handle_send_message(user_id, text):
                return

        # Команда "чат N"
        if text.startswith("чат ") or text.startswith("chat "):
            try:
                match_num = int(text.split()[1])
                from data_storage import get_matches

                if 1 <= match_num <= len(get_matches(user_id)):
                    handle_start_chat(user_id, match_num)
                else:
                    send_message(user_id, "❌ Неверный номер мэтча")
            except (ValueError, IndexError):
                send_message(user_id, "❌ Используйте: чат 1")
            return

        # Ввод для настроек/рассылки
        if state and state.get("mode") in [
            "waiting_age",
            "waiting_distance",
            "waiting_broadcast",
        ]:
            if handle_text_message(user_id, text):
                return

        # Убираем эмодзи
        text_clean = text
        for emoji in [
            "🚫",
            "❤️",
            "🏠",
            "🔍",
            "📊",
            "⚙️",
            "🎉",
            "🔐",
            "👥",
            "📢",
            "❌",
            "✅",
            "📅",
            "📍",
            "💬",
        ]:
            text_clean = text_clean.replace(emoji, "")
        text_clean = text_clean.strip()

        # Роутинг через словарь
        if text_clean in COMMAND_ROUTES:
            COMMAND_ROUTES[text_clean](user_id)
        else:
            send_message(user_id, "Неизвестная команда. Используй кнопки меню 👇")

    except Exception as e:
        logger.error(f"Ошибка обработки сообщения от {user_id}: {e}", exc_info=True)
        send_message(
            user_id, "⚠️ Произошла ошибка. Попробуйте позже или используйте /start"
        )


if __name__ == "__main__":
    try:
        run_bot()
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем (Ctrl+C)")
    except Exception as e:
        logger.critical(f"Критическая ошибка: {e}", exc_info=True)
        raise
