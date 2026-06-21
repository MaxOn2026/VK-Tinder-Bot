"""Модуль обработчиков команд бота."""
import random
import logging
from vk_client import get_vk_session
from keyboards import (
    create_start_keyboard,
    create_main_menu_keyboard,
    create_partner_keyboard,
    create_favorites_keyboard,
    create_blocked_keyboard,
    create_empty_list_keyboard
)
from state_manager import state_manager
from data_storage import (
    add_to_favorites as db_add_favorite,
    add_to_blocked as db_add_blocked,
    remove_from_favorites as db_remove_favorite,
    remove_from_blocked as db_remove_blocked,
    add_like,
    add_match,
    add_view,
    get_favorites,
    get_blocked,
    get_views,
    get_matches
)

# Логирование
logger = logging.getLogger(__name__)


def send_message(user_id, message, attachment=None, keyboard=None):
    """Отправляет сообщение пользователю."""
    logger.info(f"📤 Отправка сообщения пользователю {user_id}: '{message[:50]}...'")
    
    try:
        vk = get_vk_session().get_api()
        params = {
            'user_id': user_id,
            'message': message,
            'random_id': random.randint(-2147483648, 2147483647)
        }
        if attachment:
            params['attachment'] = attachment
            logger.info(f"📎 Вложение: {attachment}")
        if keyboard:
            params['keyboard'] = keyboard
            logger.info(f"️ Клавиатура добавлена")
        
        vk.messages.send(**params)
        logger.info(f"✅ Сообщение отправлено пользователю {user_id}")
        
    except Exception as e:
        logger.error(f"❌ Ошибка отправки сообщения: {e}", exc_info=True)
        raise


def handle_start(user_id):
    """Обработка приветствия и запуска поиска."""
    logger.info(f"👋 handle_start вызван для пользователя {user_id}")
    
    try:
        handle_search(user_id)
        logger.info(f"✅ handle_start завершён для {user_id}")
    except Exception as e:
        logger.error(f"❌ Ошибка в handle_start: {e}", exc_info=True)
        send_message(user_id, f"❌ Произошла ошибка: {e}")


def handle_search(user_id):
    """Обработка 'Начать поиск'."""
    from vk_search import get_user_info, search_candidates
    
    logger.info(f"🔍 handle_search вызван для пользователя {user_id}")
    
    try:
        user_info = get_user_info(user_id)
        
        if not user_info:
            send_message(user_id, "❌ Не удалось получить ваши данные. Попробуйте позже.")
            return
        
        logger.info(f"📊 Данные пользователя {user_id}:")
        logger.info(f"   Пол: {user_info['sex']} (1-жен, 2-муж)")
        logger.info(f"   Возраст: {user_info['age']}")
        logger.info(f"   Город: {user_info['city_name']} (ID: {user_info['city_id']})")
        
        candidates = search_candidates(user_info, user_id, count=20)
        
        if not candidates:
            send_message(user_id, "😔 Не нашёл подходящих людей. Попробуйте позже.")
            return
        
        state_manager.set_state(user_id, {
            'mode': 'partners',
            'candidates': candidates,
            'current_index': 0,
            'user_info': user_info
        })
        
        logger.info(f"✅ Найдено {len(candidates)} кандидатов")
        
        show_current_partner(user_id)
        
    except Exception as e:
        logger.error(f"❌ Ошибка в handle_search: {e}", exc_info=True)
        send_message(user_id, f"❌ Произошла ошибка: {e}")


def show_current_partner(user_id):
    """Показывает текущего партнёра."""
    from vk_search import format_candidate_info, get_top_photos
    
    state = state_manager.get_state(user_id)
    if not state:
        send_message(user_id, "❌ Сначала нажмите 'Начать поиск'")
        return
    
    candidates = state['candidates']
    current_index = state['current_index']
    
    if current_index >= len(candidates):
        send_message(
            user_id,
            "😔 Все кандидаты просмотрены!",
            keyboard=create_main_menu_keyboard()
        )
        state_manager.set_state(user_id, {**state, 'mode': 'main_menu'})
        return
    
    candidate = candidates[current_index]
    candidate_id = candidate['id']
    
    # Записываем просмотр
    add_view(user_id, candidate_id)
    
    message = format_candidate_info(candidate)
    attachment = get_top_photos(candidate_id, count=3)
    keyboard = create_partner_keyboard(current_index, len(candidates))
    
    send_message(user_id, message, attachment=attachment, keyboard=keyboard)
    
    logger.info(f"👤 Показан кандидат: {candidate['first_name']} {candidate['last_name']} (ID: {candidate_id})")


def handle_next(user_id):
    """Обработка 'Следующий >>'."""
    state = state_manager.get_state(user_id)
    if not state:
        send_message(user_id, "❌ Сначала нажмите 'Начать поиск'")
        return
    
    state_manager.update_index(user_id, state['current_index'] + 1)
    
    if state['mode'] == 'partners':
        show_current_partner(user_id)
    elif state['mode'] == 'favorites':
        show_current_favorite(user_id)
    elif state['mode'] == 'blocked':
        show_current_blocked(user_id)


def handle_previous(user_id):
    """Обработка '<< Предыдущий'."""
    state = state_manager.get_state(user_id)
    if not state:
        return
    
    state_manager.update_index(user_id, state['current_index'] - 1)
    
    if state['mode'] == 'partners':
        show_current_partner(user_id)
    elif state['mode'] == 'favorites':
        show_current_favorite(user_id)
    elif state['mode'] == 'blocked':
        show_current_blocked(user_id)


def handle_add_to_favorites(user_id):
    """Обработка '❤️ В избранное'."""
    state = state_manager.get_state(user_id)
    if not state:
        return
    
    candidates = state['candidates']
    current_index = state['current_index']
    
    if current_index < len(candidates):
        candidate = candidates[current_index]
        candidate_id = candidate['id']
        
        # Добавляем в БД
        added = db_add_favorite(user_id, candidate_id)
        
        if added:
            # Проверяем match
            is_match = add_like(user_id, candidate_id)
            
            if is_match:
                add_match(user_id, candidate_id)
                send_message(
                    user_id,
                    f" У вас взаимный лайк с {candidate['first_name']}! Это match!\n"
                    f"Теперь вы можете общаться друг с другом!",
                    keyboard=create_partner_keyboard(current_index, len(candidates))
                )
            else:
                send_message(
                    user_id,
                    f"❤️ {candidate['first_name']} добавлена в избранное!",
                    keyboard=create_partner_keyboard(current_index, len(candidates))
                )
        else:
            send_message(
                user_id,
                f"⚠️ {candidate['first_name']} уже в избранном",
                keyboard=create_partner_keyboard(current_index, len(candidates))
            )


def handle_add_to_blocked(user_id):
    """Обработка '🚫 В чёрный список'."""
    state = state_manager.get_state(user_id)
    if not state:
        return
    
    candidates = state['candidates']
    current_index = state['current_index']
    
    if current_index < len(candidates):
        candidate = candidates[current_index]
        candidate_id = candidate['id']
        
        added = db_add_blocked(user_id, candidate_id)
        
        if added:
            send_message(
                user_id,
                f"🚫 {candidate['first_name']} добавлена в чёрный список!",
                keyboard=create_partner_keyboard(current_index, len(candidates))
            )
        else:
            send_message(
                user_id,
                f"️ {candidate['first_name']} уже в чёрном списке",
                keyboard=create_partner_keyboard(current_index, len(candidates))
            )


def handle_main_menu(user_id):
    """Обработка '🏠 Главное меню'."""
    state_manager.set_state(user_id, {
        'mode': 'main_menu',
        'candidates': [],
        'current_index': 0
    })
    
    send_message(
        user_id,
        "🏠 Главное меню\nВыберите действие:",
        keyboard=create_main_menu_keyboard()
    )


def handle_show_partners(user_id):
    """Обработка 'Список партнёров'."""
    state = state_manager.get_state(user_id)
    if not state or not state.get('candidates'):
        send_message(
            user_id,
            "😔 Список партнёров пуст.\nСначала нажмите 'Начать поиск'",
            keyboard=create_start_keyboard()
        )
        return
    
    state_manager.set_state(user_id, {**state, 'mode': 'partners', 'current_index': 0})
    show_current_partner(user_id)


def handle_show_favorites(user_id):
    """Обработка 'Список избранных'."""
    favorites_ids = get_favorites(user_id)
    
    if not favorites_ids:
        send_message(
            user_id,
            "📭 Список избранных пуст",
            keyboard=create_main_menu_keyboard()
        )
        return
    
    # Получаем данные избранных из VK API
    vk_user = get_vk_session().get_api()
    
    try:
        users_data = vk_user.users.get(user_ids=favorites_ids[:10], fields='sex,city,bdate')
        
        state_manager.set_state(user_id, {
            'mode': 'favorites',
            'favorites_list': users_data,
            'current_index': 0
        })
        
        show_current_favorite(user_id)
        
    except Exception as e:
        logger.error(f"❌ Ошибка получения данных избранных: {e}")
        send_message(user_id, "❌ Не удалось загрузить список избранных")


def show_current_favorite(user_id):
    """Показывает текущего избранного."""
    state = state_manager.get_state(user_id)
    if not state:
        return
    
    favorites = state.get('favorites_list', [])
    current_index = state['current_index']
    
    if current_index >= len(favorites):
        send_message(
            user_id,
            " Больше нет избранных",
            keyboard=create_main_menu_keyboard()
        )
        return
    
    favorite = favorites[current_index]
    
    first_name = favorite.get('first_name', '')
    last_name = favorite.get('last_name', '')
    favorite_id = favorite['id']
    profile_link = f"https://vk.com/id{favorite_id}"
    
    age_text = ""
    if 'bdate' in favorite:
        try:
            parts = favorite['bdate'].split('.')
            if len(parts) == 3:
                age = 2026 - int(parts[2])
                age_text = f", {age} лет"
        except:
            pass
    
    city_text = ""
    if 'city' in favorite:
        city_text = f", {favorite['city'].get('title', '')}"
    
    message = f"❤️ {first_name} {last_name}{age_text}{city_text}\n🔗 {profile_link}\n📊 {current_index + 1} из {len(favorites)}"
    
    keyboard = create_favorites_keyboard(current_index, len(favorites))
    
    send_message(user_id, message, keyboard=keyboard)


def handle_show_blocked(user_id):
    """Обработка 'Чёрный список'."""
    blocked_ids = get_blocked(user_id)
    
    if not blocked_ids:
        send_message(
            user_id,
            "📭 Чёрный список пуст",
            keyboard=create_main_menu_keyboard()
        )
        return
    
    vk_user = get_vk_session().get_api()
    
    try:
        users_data = vk_user.users.get(user_ids=blocked_ids[:10], fields='sex,city,bdate')
        
        state_manager.set_state(user_id, {
            'mode': 'blocked',
            'blocked_list': users_data,
            'current_index': 0
        })
        
        show_current_blocked(user_id)
        
    except Exception as e:
        logger.error(f"❌ Ошибка получения данных чёрного списка: {e}")
        send_message(user_id, "❌ Не удалось загрузить чёрный список")


def show_current_blocked(user_id):
    """Показывает текущего заблокированного."""
    state = state_manager.get_state(user_id)
    if not state:
        return
    
    blocked = state.get('blocked_list', [])
    current_index = state['current_index']
    
    if current_index >= len(blocked):
        send_message(
            user_id,
            " Больше нет заблокированных",
            keyboard=create_main_menu_keyboard()
        )
        return
    
    blocked_user = blocked[current_index]
    
    first_name = blocked_user.get('first_name', '')
    last_name = blocked_user.get('last_name', '')
    blocked_id = blocked_user['id']
    profile_link = f"https://vk.com/id{blocked_id}"
    
    age_text = ""
    if 'bdate' in blocked_user:
        try:
            parts = blocked_user['bdate'].split('.')
            if len(parts) == 3:
                age = 2026 - int(parts[2])
                age_text = f", {age} лет"
        except:
            pass
    
    city_text = ""
    if 'city' in blocked_user:
        city_text = f", {blocked_user['city'].get('title', '')}"
    
    message = f" {first_name} {last_name}{age_text}{city_text}\n🔗 {profile_link}\n📊 {current_index + 1} из {len(blocked)}"
    
    keyboard = create_blocked_keyboard(current_index, len(blocked))
    
    send_message(user_id, message, keyboard=keyboard)


def handle_remove_from_favorites(user_id):
    """Обработка '❌ Удалить из избранного'."""
    state = state_manager.get_state(user_id)
    if not state:
        return
    
    favorites_list = state.get('favorites_list', [])
    current_index = state['current_index']
    
    if current_index < len(favorites_list):
        favorite = favorites_list[current_index]
        candidate_id = favorite['id']
        
        removed = db_remove_favorite(user_id, candidate_id)
        
        if removed:
            send_message(
                user_id,
                f"❌ {favorite['first_name']} удалена из избранного",
                keyboard=create_main_menu_keyboard()
            )
        else:
            send_message(
                user_id,
                f"⚠️ {favorite['first_name']} не в избранном",
                keyboard=create_main_menu_keyboard()
            )


def handle_remove_from_blocked(user_id):
    """Обработка '✅ Удалить из чёрного списка'."""
    state = state_manager.get_state(user_id)
    if not state:
        return
    
    blocked_list = state.get('blocked_list', [])
    current_index = state['current_index']
    
    if current_index < len(blocked_list):
        blocked_user = blocked_list[current_index]
        candidate_id = blocked_user['id']
        
        removed = db_remove_blocked(user_id, candidate_id)
        
        if removed:
            send_message(
                user_id,
                f"✅ {blocked_user['first_name']} удалена из чёрного списка",
                keyboard=create_main_menu_keyboard()
            )
        else:
            send_message(
                user_id,
                f"⚠️ {blocked_user['first_name']} не в чёрном списке",
                keyboard=create_main_menu_keyboard()
            )


def handle_statistics(user_id):
    """Обработка '📊 Статистика'."""
    views = len(get_views(user_id))
    favorites = len(get_favorites(user_id))
    blocked = len(get_blocked(user_id))
    matches = len(get_matches(user_id))
    
    message = (
        f"📊 Ваша статистика:\n\n"
        f"👁 Просмотрено анкет: {views}\n"
        f"❤️ В избранном: {favorites}\n"
        f"🚫 Заблокировано: {blocked}\n"
        f"🎉 Взаимных лайков: {matches}\n\n"
        f"Продолжайте искать свою половинку! 💕"
    )
    
    send_message(user_id, message, keyboard=create_main_menu_keyboard())


def handle_unknown(user_id):
    """Обработка неизвестной команды."""
    send_message(
        user_id,
        "❓ Неизвестная команда.\nИспользуйте кнопки меню 👇",
        keyboard=create_main_menu_keyboard()
    )