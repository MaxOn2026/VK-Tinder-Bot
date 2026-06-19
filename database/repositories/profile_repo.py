"""Репозиторий для работы с профилями VK."""
from typing import Optional, Dict, Any, List
from sqlalchemy import select
from database.db_manager import db_manager
from database.models.profile import VKProfile


def get_profile(vk_id: int) -> Optional[VKProfile]:
    """Получает профиль по vk_id.

    Args:
        vk_id: ID пользователя ВКонтакте.

    Returns:
        Optional[VKProfile]: Объект профиля или None.
    """
    with db_manager.get_session() as session:
        return session.execute(
            select(VKProfile).where(VKProfile.vk_id == vk_id)
        ).scalar_one_or_none()


def get_or_create_profile(
    vk_id: int,
    first_name: str = "",
    last_name: str = "",
    birth_year: Optional[int] = None,
    gender: int = 0,
    city: Optional[str] = None,
) -> VKProfile:
    """Получает профиль из БД или создаёт новый.

    Args:
        vk_id: ID пользователя ВКонтакте.
        first_name: Имя.
        last_name: Фамилия.
        birth_year: Год рождения.
        gender: Пол (0-не указан, 1-женщина, 2-мужчина).
        city: Город.

    Returns:
        VKProfile: Объект профиля.
    """
    with db_manager.get_session() as session:
        profile = session.execute(
            select(VKProfile).where(VKProfile.vk_id == vk_id)
        ).scalar_one_or_none()

        if profile is None:
            profile = VKProfile(
                vk_id=vk_id,
                first_name=first_name or "Неизвестно",
                last_name=last_name or "",
                birth_year=birth_year,
                gender=gender,
                city=city,
            )
            session.add(profile)

        return profile


def update_profile(
    vk_id: int,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    birth_year: Optional[int] = None,
    gender: Optional[int] = None,
    city: Optional[str] = None,
    relation: Optional[int] = None,
    education: Optional[str] = None,
) -> bool:
    """Обновляет данные профиля.

    Args:
        vk_id: ID пользователя ВКонтакте.
        first_name: Имя.
        last_name: Фамилия.
        birth_year: Год рождения.
        gender: Пол.
        city: Город.
        relation: Семейное положение.
        education: Образование.

    Returns:
        bool: True если обновлено, False если профиль не найден.
    """
    with db_manager.get_session() as session:
        profile = session.execute(
            select(VKProfile).where(VKProfile.vk_id == vk_id)
        ).scalar_one_or_none()

        if profile is None:
            return False

        if first_name is not None:
            profile.first_name = first_name
        if last_name is not None:
            profile.last_name = last_name
        if birth_year is not None:
            profile.birth_year = birth_year
        if gender is not None:
            profile.gender = gender
        if city is not None:
            profile.city = city
        if relation is not None:
            profile.relation = relation
        if education is not None:
            profile.education = education

        return True


def save_candidate(candidate_data: Dict[str, Any]) -> Optional[VKProfile]:
    """Сохраняет кандидата из результатов поиска VK в БД.

    Args:
        candidate_data: Словарь с данными кандидата от VK API.

    Returns:
        Optional[VKProfile]: Сохранённый профиль или None.
    """
    vk_id = candidate_data.get('id')
    if not vk_id:
        return None

    first_name = candidate_data.get('first_name', '')
    last_name = candidate_data.get('last_name', '')

    birth_year = None
    bdate = candidate_data.get('bdate')
    if bdate:
        try:
            parts = bdate.split('.')
            if len(parts) == 3:
                birth_year = int(parts[2])
        except:
            pass

    gender = candidate_data.get('sex', 0)

    city = None
    if 'city' in candidate_data:
        city_data = candidate_data['city']
        if isinstance(city_data, dict):
            city = city_data.get('title')
        elif isinstance(city_data, str):
            city = city_data

    with db_manager.get_session() as session:
        profile = session.execute(
            select(VKProfile).where(VKProfile.vk_id == vk_id)
        ).scalar_one_or_none()

        if profile is None:
            profile = VKProfile(
                vk_id=vk_id,
                first_name=first_name,
                last_name=last_name,
                birth_year=birth_year,
                gender=gender,
                city=city,
            )
            session.add(profile)
        else:
            # Обновляем данные, если они стали полнее
            if not profile.first_name and first_name:
                profile.first_name = first_name
            if not profile.last_name and last_name:
                profile.last_name = last_name
            if profile.birth_year is None and birth_year is not None:
                profile.birth_year = birth_year
            if profile.gender == 0 and gender != 0:
                profile.gender = gender
            if profile.city is None and city:
                profile.city = city

        return profile


def get_profiles_by_city(city: str) -> List[VKProfile]:
    """Получает профили по городу.

    Args:
        city: Название города.

    Returns:
        List[VKProfile]: Список профилей.
    """
    with db_manager.get_session() as session:
        return list(session.execute(
            select(VKProfile).where(VKProfile.city == city)
        ).scalars().all())


def get_profiles_by_gender(gender: int) -> List[VKProfile]:
    """Получает профили по полу.

    Args:
        gender: Пол (1-женщина, 2-мужчина).

    Returns:
        List[VKProfile]: Список профилей.
    """
    with db_manager.get_session() as session:
        return list(session.execute(
            select(VKProfile).where(VKProfile.gender == gender)
        ).scalars().all())


def search_profiles(
    gender: Optional[int] = None,
    city: Optional[str] = None,
    birth_year_min: Optional[int] = None,
    birth_year_max: Optional[int] = None,
    limit: int = 50,
) -> List[VKProfile]:
    """Ищет профили по критериям.

    Args:
        gender: Пол (1-женщина, 2-мужчина).
        city: Город.
        birth_year_min: Минимальный год рождения.
        birth_year_max: Максимальный год рождения.
        limit: Максимальное количество результатов.

    Returns:
        List[VKProfile]: Список найденных профилей.
    """
    with db_manager.get_session() as session:
        query = select(VKProfile)

        if gender is not None:
            query = query.where(VKProfile.gender == gender)
        if city is not None:
            query = query.where(VKProfile.city == city)
        if birth_year_min is not None:
            query = query.where(VKProfile.birth_year >= birth_year_min)
        if birth_year_max is not None:
            query = query.where(VKProfile.birth_year <= birth_year_max)

        query = query.limit(limit)

        return list(session.execute(query).scalars().all())
