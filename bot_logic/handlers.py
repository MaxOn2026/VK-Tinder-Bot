"""Модуль обработчиков команд бота VK-Tinder-Bot.

Этот модуль содержит все функции-обработчики для команд бота ВКонтакте:
приветствие, поиск партнеров, навигация по спискам, управление избранными
и черным списком. Включает функции отправки сообщений и отображения
данных пользователей.

Пример:
    ```python
    # Использование обработчика
    handle_start(user_id)
    handle_search(user_id)
    ```
"""

import random
from typing import Optional

from database.repositories.interaction_repo import (
    add_interaction,
    add_like_and_check_match,
    add_match,
    get_matches,
    get_user_interactions,
    remove_interaction,
)
from database.repositories.user_repo import get_or_create_user

from .keyboards import (
    create_blocked_keyboard,
    create_empty_list_keyboard,
    create_favorites_keyboard,
    create_main_menu_keyboard,
    create_matches_keyboard,
    create_partner_keyboard,
    create_start_keyboard,
)
from .state_manager import state_manager
from .vk_client import get_vk_session


def send_message(
    user_id: int,
    message: str,
    attachment: Optional[str] = None,
    keyboard: Optional[str] = None,
) -> None:
    """Отправляет сообщение пользователю через VK API.

    Отправляет текстовое сообщение с возможным добавлением вложения
    (фотографии) и клавиатуры для интерактивного взаимодействия.

    Args:
        user_id (int): Идентификатор получателя сообщения.
        message (str): Текст сообщения для отправки.
        attachment (str, optional): Вложение для сообщения (например, 'photo123_456').
        keyboard (str, optional): JSON-код клавиатуры для сообщения.

    Raises:
        Exception: При ошибке отправки сообщения через VK API.

    Пример:
        ```python
        # Отправка простого сообщения
        send_message(123456789, "Привет!")

        # Отправка сообщения с вложением и клавиатурой
        send_message(
            123456789,
            "Вот ваша фотография!",
            attachment="photo123_456",
            keyboard=keyboard_json
        )
        ```
    """
    vk = get_vk_session().get_api()
    params = {
        "user_id": user_id,
        "message": message,
        "random_id": random.randint(-2147483648, 2147483647),
    }
    if attachment:
        params["attachment"] = attachment
    if keyboard:
        params["keyboard"] = keyboard

    vk.messages.send(**params)


def handle_start(user_id: int) -> None:
    """Обрабатывает команду приветствия и начало работы с ботом.

    Регистрирует нового пользователя в базе данных и отправляет
    приветственное сообщение с инструкцией и клавиатурой.

    Args:
        user_id (int): Идентификатор пользователя ВКонтакте.

    Returns:
        None

    Raises:
        Exception: При ошибке регистрации пользователя в БД.

    Пример:
        ```python
        # Обработка команды приветствия
        handle_start(user_id=123456789)
        ```
    """
    # Регистрация пользователя в БД
    get_or_create_user(user_id)

    send_message(
        user_id,
        "Привет! Я VKinder Bot. Найду тебе пару! 👇",
        keyboard=create_start_keyboard(),
    )


def handle_search(user_id: int) -> None:
    """Обрабатывает команду начала поиска партнеров.

    Инициирует процесс поиска партнеров на основе данных пользователя:
    получает информацию из VK API, обновляет предпочтения в БД,
    выполняет поиск подходящих кандидатов и сохраняет состояние
    пользователя для навигации по списку.

    Args:
        user_id (int): Идентификатор пользователя ВКонтакте.

    Returns:
        None

    Raises:
        Exception: При ошибке получения данных из VK API или БД.

    Пример:
        ```python
        # Начало поиска партнеров
        handle_search(user_id=123456789)
        ```
    """
    from database.repositories.profile_repo import get_or_create_profile
    from database.repositories.user_repo import get_user

    from .vk_search import search_candidates

    # Получаем или создаём пользователя с данными из VK
    get_or_create_user(user_id)

    # Получаем данные из БД (они уже подтянуты из VK при создании)
    bot_user = get_user(user_id)

    if not bot_user:
        send_message(user_id, "❌ Не удалось получить ваши данные. Попробуйте позже.")
        return

    # Получаем информацию из VK для поиска
    from .vk_search import get_user_info

    user_info = get_user_info(user_id)

    if not user_info:
        send_message(user_id, "❌ Не удалось получить ваши данные. Попробуйте позже.")
        return

    # Обновляем предпочтения в БД из актуальных данных VK
    from datetime import date

    birth_year = None
    if user_info.get("age"):
        birth_year = date.today().year - user_info["age"]

    get_or_create_profile(
        vk_id=user_id,
        birth_year=birth_year,
        gender=user_info.get("sex", 0),
        city=user_info.get("city_name"),
    )

    print(f"📊 Данные пользователя {user_id}:")
    print(f"   Пол: {user_info['sex']} (1-жен, 2-муж)")
    print(f"   Возраст: {user_info['age']}")
    print(f"   Город: {user_info['city_name']} (ID: {user_info['city_id']})")

    candidates = search_candidates(user_info, user_id, count=20)

    if not candidates:
        send_message(user_id, " Не нашёл подходящих людей. Попробуйте позже.")
        return

    state_manager.set_state(
        user_id,
        {
            "mode": "partners",
            "candidates": candidates,
            "current_index": 0,
            "user_info": user_info,
        },
    )

    print(f"✅ Найдено {len(candidates)} кандидатов")

    show_current_partner(user_id)


def show_current_partner(user_id: int) -> None:
    """Отображает текущего кандидата из списка партнеров.

    Получает текущего кандидата из состояния пользователя, формирует
    сообщение с информацией о нем и фотографиями, отправляет сообщение
    пользователю и обновляет состояние.

    Args:
        user_id (int): Идентификатор пользователя ВКонтакте.

    Returns:
        None

    Raises:
        Exception: При ошибке формирования сообщения или отправки.

    Пример:
        ```python
        # Показ текущего партнера
        show_current_partner(user_id=123456789)
        ```
    """
    from .vk_search import format_candidate_info, get_top_photos

    state = state_manager.get_state(user_id)
    if not state:
        send_message(user_id, "❌ Сначала нажмите 'Начать поиск'")
        return

    candidates = state["candidates"]
    current_index = state["current_index"]

    if current_index >= len(candidates):
        send_message(
            user_id, " Все кандидаты просмотрены!", keyboard=create_main_menu_keyboard()
        )
        state_manager.set_state(user_id, {**state, "mode": "main_menu"})
        return

    candidate = candidates[current_index]
    candidate_id = candidate["id"]

    # Записываем просмотр в БД
    add_interaction(user_id, candidate_id, "view")

    message = format_candidate_info(candidate)
    attachment = get_top_photos(candidate_id, count=3)
    keyboard = create_partner_keyboard(current_index, len(candidates))

    send_message(user_id, message, attachment=attachment, keyboard=keyboard)

    print(
        f" Показан кандидат: {candidate['first_name']} {candidate['last_name']} (ID: {candidate_id})"
    )


def handle_next(user_id: int) -> None:
    """Обрабатывает команду перехода к следующему кандидату.

    Обновляет текущий индекс в состоянии пользователя и отображает
    следующего кандидата в зависимости от текущего режима (partners,
    favorites, blocked, matches).

    Args:
        user_id (int): Идентификатор пользователя ВКонтакте.

    Returns:
        None

    Raises:
        Exception: При ошибке обновления состояния или отображения.

    Пример:
        ```python
        # Переход к следующему кандидату
        handle_next(user_id=123456789)
        ```
    """
    state = state_manager.get_state(user_id)
    if not state:
        send_message(user_id, " Сначала нажмите 'Начать поиск'")
        return

    state_manager.update_index(user_id, state["current_index"] + 1)

    if state["mode"] == "partners":
        show_current_partner(user_id)
    elif state["mode"] == "favorites":
        show_current_favorite(user_id)
    elif state["mode"] == "blocked":
        show_current_blocked(user_id)
    elif state["mode"] == "matches":
        show_current_match(user_id)


def handle_previous(user_id: int) -> None:
    """Обрабатывает команду перехода к предыдущему кандидату.

    Обновляет текущий индекс в состоянии пользователя и отображает
    предыдущего кандидата в зависимости от текущего режима.

    Args:
        user_id (int): Идентификатор пользователя ВКонтакте.

    Returns:
        None

    Raises:
        Exception: При ошибке обновления состояния или отображения.

    Пример:
        ```python
        # Переход к предыдущему кандидату
        handle_previous(user_id=123456789)
        ```
    """
    state = state_manager.get_state(user_id)
    if not state:
        return

    state_manager.update_index(user_id, state["current_index"] - 1)

    if state["mode"] == "partners":
        show_current_partner(user_id)
    elif state["mode"] == "favorites":
        show_current_favorite(user_id)
    elif state["mode"] == "blocked":
        show_current_blocked(user_id)
    elif state["mode"] == "matches":
        show_current_match(user_id)


def handle_add_to_favorites(user_id: int) -> None:
    """Обрабатывает команду добавления кандидата в избранное.

    Добавляет текущего кандидата в список избранных пользователя,
    проверяет наличие взаимного лайка и уведомляет пользователя
    о результате (match или просто добавление в избранное).

    Args:
        user_id (int): Идентификатор пользователя ВКонтакте.

    Returns:
        None

    Raises:
        Exception: При ошибке добавления в БД или проверки матча.

    Пример:
        ```python
        # Добавление в избранное
        handle_add_to_favorites(user_id=123456789)
        ```
    """
    state = state_manager.get_state(user_id)
    if not state:
        return

    candidates = state["candidates"]
    current_index = state["current_index"]

    if current_index < len(candidates):
        candidate = candidates[current_index]
        candidate_id = candidate["id"]

        # Добавляем в БД
        added = add_interaction(user_id, candidate_id, "like")

        if added:
            # Проверяем match
            is_match = add_like_and_check_match(user_id, candidate_id)

            if is_match:
                add_match(user_id, candidate_id)
                send_message(
                    user_id,
                    f"🎉 У вас взаимный лайк с {candidate['first_name']}! Это match!",
                    keyboard=create_partner_keyboard(current_index, len(candidates)),
                )
            else:
                send_message(
                    user_id,
                    f"❤️ {candidate['first_name']} добавлена в избранное!",
                    keyboard=create_partner_keyboard(current_index, len(candidates)),
                )
        else:
            send_message(
                user_id,
                f"⚠️ {candidate['first_name']} уже в избранном",
                keyboard=create_partner_keyboard(current_index, len(candidates)),
            )


def handle_add_to_blocked(user_id: int) -> None:
    """Обрабатывает команду добавления кандидата в черный список.

    Добавляет текущего кандидата в черный список пользователя
    и уведомляет о результате операции.

    Args:
        user_id (int): Идентификатор пользователя ВКонтакте.

    Returns:
        None

    Raises:
        Exception: При ошибке добавления в черный список.

    Пример:
        ```python
        # Добавление в черный список
        handle_add_to_blocked(user_id=123456789)
        ```
    """
    state = state_manager.get_state(user_id)
    if not state:
        return

    candidates = state["candidates"]
    current_index = state["current_index"]

    if current_index < len(candidates):
        candidate = candidates[current_index]
        candidate_id = candidate["id"]

        added = add_interaction(user_id, candidate_id, "block")

        if added:
            send_message(
                user_id,
                f"🚫 {candidate['first_name']} добавлена в чёрный список!",
                keyboard=create_partner_keyboard(current_index, len(candidates)),
            )
        else:
            send_message(
                user_id,
                f"⚠️ {candidate['first_name']} уже в чёрном списке",
                keyboard=create_partner_keyboard(current_index, len(candidates)),
            )


def handle_main_menu(user_id: int) -> None:
    """Обрабатывает команду возврата в главное меню.

    Сбрасывает состояние пользователя до главного меню и отправляет
    соответствующее сообщение с клавиатурой главного меню.

    Args:
        user_id (int): Идентификатор пользователя ВКонтакте.

    Returns:
        None

    Raises:
        Exception: При ошибке обновления состояния.

    Пример:
        ```python
        # Возврат в главное меню
        handle_main_menu(user_id=123456789)
        ```
    """
    state_manager.set_state(
        user_id, {"mode": "main_menu", "candidates": [], "current_index": 0}
    )

    send_message(
        user_id,
        "🏠 Главное меню\nВыберите действие:",
        keyboard=create_main_menu_keyboard(),
    )


def handle_show_partners(user_id: int) -> None:
    """Обрабатывает команду отображения списка партнеров.

    Отображает список партнеров, если он уже был сгенерирован,
    или направляет пользователя к началу поиска.

    Args:
        user_id (int): Идентификатор пользователя ВКонтакте.

    Returns:
        None

    Raises:
        Exception: При ошибке отображения списка партнеров.

    Пример:
        ```python
        # Показ списка партнеров
        handle_show_partners(user_id=123456789)
        ```
    """
    state = state_manager.get_state(user_id)
    if not state or not state.get("candidates"):
        send_message(
            user_id,
            " Список партнеров пуст.\nСначала нажмите 'Начать поиск'",
            keyboard=create_start_keyboard(),
        )
        return

    state_manager.set_state(user_id, {**state, "mode": "partners", "current_index": 0})
    show_current_partner(user_id)


def handle_show_favorites(user_id: int) -> None:
    """Обрабатывает команду отображения списка избранных.

    Загружает список избранных пользователей из базы данных,
    получает актуальные данные из VK API и отображает первого
    избранный в списке.

    Args:
        user_id (int): Идентификатор пользователя ВКонтакте.

    Returns:
        None

    Raises:
        Exception: При ошибке загрузки данных из БД или VK API.

    Пример:
        ```python
        # Показ списка избранных
        handle_show_favorites(user_id=123456789)
        ```
    """
    # Загружаем из БД
    favorites_ids = get_user_interactions(user_id, action="like")

    if not favorites_ids:
        send_message(
            user_id, "📭 Список избранных пуст", keyboard=create_main_menu_keyboard()
        )
        return

    # Получаем данные избранных из VK API
    from .vk_search import get_user_info

    vk_user = get_vk_session().get_api()

    try:
        users_data = vk_user.users.get(
            user_ids=favorites_ids[:10], fields="sex,city,bdate"
        )

        state_manager.set_state(
            user_id,
            {"mode": "favorites", "favorites_list": users_data, "current_index": 0},
        )

        show_current_favorite(user_id)

    except Exception as e:
        print(f"❌ Ошибка получения данных избранных: {e}")
        send_message(user_id, "❌ Не удалось загрузить список избранных")


def show_current_favorite(user_id: int) -> None:
    """Отображает текущего избранного пользователя.

    Формирует сообщение с информацией об избранном пользователе
    (имя, возраст, город, ссылка на профиль) и отправляет его.

    Args:
        user_id (int): Идентификатор пользователя ВКонтакте.

    Returns:
        None

    Raises:
        Exception: При ошибке формирования или отправки сообщения.

    Пример:
        ```python
        # Показ текущего избранного
        show_current_favorite(user_id=123456789)
        ```
    """
    state = state_manager.get_state(user_id)
    if not state:
        return

    favorites = state.get("favorites_list", [])
    current_index = state["current_index"]

    if current_index >= len(favorites):
        send_message(
            user_id, "📭 Больше нет избранных", keyboard=create_main_menu_keyboard()
        )
        return

    favorite = favorites[current_index]

    first_name = favorite.get("first_name", "")
    last_name = favorite.get("last_name", "")
    favorite_id = favorite["id"]
    profile_link = f"https://vk.com/id{favorite_id}"

    age_text = ""
    if "bdate" in favorite:
        try:
            parts = favorite["bdate"].split(".")
            if len(parts) == 3:
                age = 2026 - int(parts[2])
                age_text = f", {age} лет"
        except:
            pass

    city_text = ""
    if "city" in favorite:
        city_text = f", {favorite['city'].get('title', '')}"

    message = f"❤️ {first_name} {last_name}{age_text}{city_text}\n🔗 {profile_link}\n {current_index + 1} из {len(favorites)}"

    keyboard = create_favorites_keyboard(current_index, len(favorites))

    send_message(user_id, message, keyboard=keyboard)


def handle_show_blocked(user_id: int) -> None:
    """Обрабатывает команду отображения черного списка.

    Загружает список заблокированных пользователей из базы данных,
    получает данные из VK API и отображает первого заблокированного.

    Args:
        user_id (int): Идентификатор пользователя ВКонтакте.

    Returns:
        None

    Raises:
        Exception: При ошибке загрузки данных из БД или VK API.

    Пример:
        ```python
        # Показ черного списка
        handle_show_blocked(user_id=123456789)
        ```
    """
    # Загружаем из БД
    blocked_ids = get_user_interactions(user_id, action="block")

    if not blocked_ids:
        send_message(
            user_id, "📭 Чёрный список пуст", keyboard=create_main_menu_keyboard()
        )
        return

    vk_user = get_vk_session().get_api()

    try:
        users_data = vk_user.users.get(
            user_ids=blocked_ids[:10], fields="sex,city,bdate"
        )

        state_manager.set_state(
            user_id, {"mode": "blocked", "blocked_list": users_data, "current_index": 0}
        )

        show_current_blocked(user_id)

    except Exception as e:
        print(f"❌ Ошибка получения данных чёрного списка: {e}")
        send_message(user_id, "❌ Не удалось загрузить чёрный список")


def show_current_blocked(user_id: int) -> None:
    """Отображает текущего заблокированного пользователя.

    Формирует сообщение с информацией о заблокированном пользователе
    и отправляет его с соответствующей клавиатурой.

    Args:
        user_id (int): Идентификатор пользователя ВКонтакте.

    Returns:
        None

    Raises:
        Exception: При ошибке формирования или отправки сообщения.

    Пример:
        ```python
        # Показ текущего заблокированного
        show_current_blocked(user_id=123456789)
        ```
    """
    state = state_manager.get_state(user_id)
    if not state:
        return

    blocked = state.get("blocked_list", [])
    current_index = state["current_index"]

    if current_index >= len(blocked):
        send_message(
            user_id,
            "📭 Больше нет заблокированных",
            keyboard=create_main_menu_keyboard(),
        )
        return

    blocked_user = blocked[current_index]

    first_name = blocked_user.get("first_name", "")
    last_name = blocked_user.get("last_name", "")
    blocked_id = blocked_user["id"]
    profile_link = f"https://vk.com/id{blocked_id}"

    age_text = ""
    if "bdate" in blocked_user:
        try:
            parts = blocked_user["bdate"].split(".")
            if len(parts) == 3:
                age = 2026 - int(parts[2])
                age_text = f", {age} лет"
        except:
            pass

    city_text = ""
    if "city" in blocked_user:
        city_text = f", {blocked_user['city'].get('title', '')}"

    message = f"🚫 {first_name} {last_name}{age_text}{city_text}\n🔗 {profile_link}\n📊 {current_index + 1} из {len(blocked)}"

    keyboard = create_blocked_keyboard(current_index, len(blocked))

    send_message(user_id, message, keyboard=keyboard)


def handle_remove_from_favorites(user_id: int) -> None:
    """Обрабатывает команду удаления из избранного.

    Удаляет текущего избранного пользователя из списка избранных
    в базе данных и уведомляет пользователя о результате.

    Args:
        user_id (int): Идентификатор пользователя ВКонтакте.

    Returns:
        None

    Raises:
        Exception: При ошибке удаления из БД.

    Пример:
        ```python
        # Удаление из избранного
        handle_remove_from_favorites(user_id=123456789)
        ```
    """
    state = state_manager.get_state(user_id)
    if not state:
        return

    favorites_list = state.get("favorites_list", [])
    current_index = state["current_index"]

    if current_index < len(favorites_list):
        favorite = favorites_list[current_index]
        candidate_id = favorite["id"]

        # Удаляем из БД
        removed = remove_interaction(user_id, candidate_id, "like")

        send_message(
            user_id,
            f"❌ {favorite['first_name']} удалена из избранного",
            keyboard=create_main_menu_keyboard(),
        )
    else:
        send_message(user_id, f"⚠️ Нечего удалять", keyboard=create_main_menu_keyboard())


def handle_remove_from_blocked(user_id: int) -> None:
    """Обрабатывает команду удаления из черного списка.

    Удаляет текущего заблокированного пользователя из черного списка
    в базе данных и уведомляет пользователя о результате.

    Args:
        user_id (int): Идентификатор пользователя ВКонтакте.

    Returns:
        None

    Raises:
        Exception: При ошибке удаления из БД.

    Пример:
        ```python
        # Удаление из черного списка
        handle_remove_from_blocked(user_id=123456789)
        ```
    """
    state = state_manager.get_state(user_id)
    if not state:
        return

    blocked_list = state.get("blocked_list", [])
    current_index = state["current_index"]

    if current_index < len(blocked_list):
        blocked_user = blocked_list[current_index]
        candidate_id = blocked_user["id"]

        # Удаляем из БД
        removed = remove_interaction(user_id, candidate_id, "block")

        send_message(
            user_id,
            f"✅ {blocked_user['first_name']} удалена из чёрного списка",
            keyboard=create_main_menu_keyboard(),
        )
    else:
        send_message(user_id, f"⚠️ Нечего удалять", keyboard=create_main_menu_keyboard())


def handle_show_matches(user_id: int) -> None:
    """Обрабатывает команду отображения списка матчей.

    Загружает список пользователей, с которыми есть взаимный лайк
    (матчи), получает данные из VK API и отображает первого матча.

    Args:
        user_id (int): Идентификатор пользователя ВКонтакте.

    Returns:
        None

    Raises:
        Exception: При ошибке загрузки данных из БД или VK API.

    Пример:
        ```python
        # Показ списка матчей
        handle_show_matches(user_id=123456789)
        ```
    """
    match_ids = get_matches(user_id)

    if not match_ids:
        send_message(
            user_id, "📭 Список матчей пуст", keyboard=create_main_menu_keyboard()
        )
        return

    vk_user = get_vk_session().get_api()

    try:
        users_data = vk_user.users.get(user_ids=match_ids[:20], fields="sex,city,bdate")

        state_manager.set_state(
            user_id, {"mode": "matches", "matches_list": users_data, "current_index": 0}
        )

        show_current_match(user_id)

    except Exception as e:
        print(f"❌ Ошибка получения данных матчей: {e}")
        send_message(user_id, "❌ Не удалось загрузить список матчей")


def show_current_match(user_id: int) -> None:
    """Отображает текущего матча (пользователя с взаимным лайком).

    Формирует сообщение с информацией о матче и отправляет его
    с соответствующей клавиатурой.

    Args:
        user_id (int): Идентификатор пользователя ВКонтакте.

    Returns:
        None

    Raises:
        Exception: При ошибке формирования или отправки сообщения.

    Пример:
        ```python
        # Показ текущего матча
        show_current_match(user_id=123456789)
        ```
    """
    state = state_manager.get_state(user_id)
    if not state:
        return

    matches = state.get("matches_list", [])
    current_index = state["current_index"]

    if current_index >= len(matches):
        send_message(
            user_id, "📭 Больше нет матчей", keyboard=create_main_menu_keyboard()
        )
        state_manager.set_state(user_id, {**state, "mode": "main_menu"})
        return

    match_user = matches[current_index]

    first_name = match_user.get("first_name", "")
    last_name = match_user.get("last_name", "")
    match_id = match_user["id"]
    profile_link = f"https://vk.com/id{match_id}"

    age_text = ""
    if "bdate" in match_user:
        try:
            parts = match_user["bdate"].split(".")
            if len(parts) == 3:
                age = 2026 - int(parts[2])
                age_text = f", {age} лет"
        except:
            pass

    city_text = ""
    if "city" in match_user:
        city_text = f", {match_user['city'].get('title', '')}"

    parts = []
    parts.append(f"🎉 {first_name} {last_name}{age_text}{city_text}")
    parts.append(f"🔗 {profile_link}")
    parts.append(f"📊 {current_index + 1} из {len(matches)}")
    message = "\n".join(parts)

    keyboard = create_matches_keyboard(current_index, len(matches))

    send_message(user_id, message, keyboard=keyboard)
