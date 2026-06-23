"""Репозиторий для работы с пользователями бота."""

from datetime import date
from typing import Any, Dict, Optional

from sqlalchemy import select

from database.db_manager import db_manager
from database.models.user import BotUser

DEFAULT_USER_NAME = "Пользователь"


def _fetch_vk_user_data(vk_id: int) -> Optional[Dict[str, Any]]:
    """Получает данные пользователя из VK API.

    Args:
        vk_id: ID пользователя ВКонтакте.

    Returns:
        Optional[Dict[str, Any]]: Словарь с данными или None.
    """
    try:
        from bot_logic.vk_client import get_vk_user_session

        vk = get_vk_user_session().get_api()
        users = vk.users.get(user_ids=vk_id, fields="sex,city,bdate")
        if users:
            user = users[0]
            return {
                "first_name": user.get("first_name", ""),
                "last_name": user.get("last_name", ""),
                "gender": user.get("sex", 0),
                "city": user.get("city", {}).get("title")
                if isinstance(user.get("city"), dict)
                else None,
                "bdate": user.get("bdate"),
            }
    except Exception as e:
        print(f"⚠️ Ошибка получения данных VK для vk_id={vk_id}: {e}")
    return None


def _parse_birthdate(bdate_str: str) -> Optional[date]:
    """Парсит строку даты в формате ДД.ММ.ГГГГ в объект date."""
    try:
        parts = bdate_str.split(".")
        if len(parts) == 3:
            return date(int(parts[2]), int(parts[1]), int(parts[0]))
    except (ValueError, IndexError):
        pass
    return None


def _determine_looking_for(gender: int) -> int:
    """Определяет, кого ищет пользователь (мужчина ищет женщину, и наоборот)."""
    return 2 if gender == 1 else 1


def _create_user_from_vk(vk_id: int, vk_data: Dict[str, Any]) -> BotUser:
    """Создаёт нового пользователя в БД на основе данных из VK."""
    gender = vk_data["gender"]
    looking_for = _determine_looking_for(gender)

    user = BotUser(
        vk_id=vk_id,
        name=vk_data["first_name"] or DEFAULT_USER_NAME,
        surname=vk_data["last_name"] or "",
        gender=gender,
        looking_for=looking_for,
        city=vk_data["city"],
    )

    if vk_data["bdate"]:
        user.birthdate = _parse_birthdate(vk_data["bdate"])

    print(f"🆕 Создан пользователь в БД: vk_id={vk_id} ({user.name} {user.surname})")
    return user


def _update_user_name(user: BotUser, vk_data: Dict[str, Any]) -> None:
    """Обновляет имя/фамилию пользователя, если они пустые."""
    needs_update = False

    if user.name in ("", DEFAULT_USER_NAME) and vk_data["first_name"]:
        user.name = vk_data["first_name"]
        needs_update = True

    if user.surname == "" and vk_data["last_name"]:
        user.surname = vk_data["last_name"]
        needs_update = True

    if needs_update:
        print(f"🔄 Обновлены данные пользователя: vk_id={user.vk_id}")


def get_or_create_user(vk_id: int) -> BotUser:
    """Получает пользователя из БД или создаёт нового с данными из VK.

    При создании автоматически подтягивает имя, фамилию, пол, город и дату рождения из VK API.

    Args:
        vk_id: ID пользователя ВКонтакте.

    Returns:
        BotUser: Объект пользователя.
    """
    with db_manager.get_session() as session:
        user = session.execute(
            select(BotUser).where(BotUser.vk_id == vk_id)
        ).scalar_one_or_none()

        if user is None:
            vk_data = _fetch_vk_user_data(vk_id)
            user = (
                _create_user_from_vk(vk_id, vk_data)
                if vk_data
                else BotUser(vk_id=vk_id, name=DEFAULT_USER_NAME, surname="")
            )
            print(
                f"🆕 Создан пользователь в БД (без данных VK): vk_id={vk_id}"
                if not vk_data
                else None
            )
            session.add(user)
        else:
            vk_data = _fetch_vk_user_data(vk_id)
            if vk_data:
                _update_user_name(user, vk_data)

        return user


def get_user(vk_id: int) -> Optional[BotUser]:
    """Получает пользователя по vk_id.

    Args:
        vk_id: ID пользователя ВКонтакте.

    Returns:
        Optional[BotUser]: Объект пользователя или None.
    """
    with db_manager.get_session() as session:
        return session.execute(
            select(BotUser).where(BotUser.vk_id == vk_id)
        ).scalar_one_or_none()


def update_user_preferences(
    vk_id: int,
    gender: Optional[int] = None,
    looking_for: Optional[int] = None,
    city: Optional[str] = None,
    age_min: Optional[int] = None,
    age_max: Optional[int] = None,
) -> bool:
    """Обновляет предпочтения пользователя.

    Args:
        vk_id: ID пользователя ВКонтакте.
        gender: Пол (0/1/2).
        looking_for: Предпочитаемый пол для знакомств.
        city: Город.
        age_min: Минимальный возраст.
        age_max: Максимальный возраст.

    Returns:
        bool: True если обновлено, False если пользователь не найден.
    """
    with db_manager.get_session() as session:
        user = session.execute(
            select(BotUser).where(BotUser.vk_id == vk_id)
        ).scalar_one_or_none()

        if user is None:
            return False

        if gender is not None:
            user.gender = gender
        if looking_for is not None:
            user.looking_for = looking_for
        if city is not None:
            user.city = city
        if age_min is not None:
            user.age_min = age_min
        if age_max is not None:
            user.age_max = age_max

        return True
