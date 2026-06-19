"""Репозиторий для взаимодействий (лайки, просмотры, блокировки)."""
from datetime import datetime
from typing import List, Optional
from sqlalchemy import select, and_
from database.db_manager import db_manager
from database.models.interaction import UserInteraction, MutualLike
from database.models.user import BotUser
from database.models.profile import VKProfile


def add_interaction(
    user_vk_id: int,
    profile_vk_id: int,
    action: str
) -> bool:
    """Добавляет взаимодействие пользователя.

    Args:
        user_vk_id: vk_id пользователя, совершившего действие.
        profile_vk_id: vk_id целевой анкеты.
        action: Тип действия (view, like, block).

    Returns:
        bool: True если добавлено, False если дубликат.
    """
    with db_manager.get_session() as session:
        user = session.execute(
            select(BotUser).where(BotUser.vk_id == user_vk_id)
        ).scalar_one_or_none()

        if user is None:
            return False

        # Проверяем, есть ли уже такое действие
        existing = session.execute(
            select(UserInteraction).where(
                and_(
                    UserInteraction.user_id == user.id,
                    UserInteraction.profile_id == profile_vk_id,
                    UserInteraction.action == action
                )
            )
        ).scalar_one_or_none()

        if existing:
            return False

        interaction = UserInteraction(
            user_id=user.id,
            profile_id=profile_vk_id,
            action=action
        )
        session.add(interaction)
        return True


def add_like_and_check_match(user_vk_id: int, profile_vk_id: int) -> bool:
    """Добавляет лайк и проверяет взаимный.

    Мэтч возможен, если профиль VK, которого лайкнули, тоже является
    зарегистрированным пользователем бота и лайкнул нас в ответ.

    Args:
        user_vk_id: vk_id поставившего лайк.
        profile_vk_id: vk_id анкеты, которую лайкнули.

    Returns:
        bool: True если взаимный лайк (match).
    """
    with db_manager.get_session() as session:
        user = session.execute(
            select(BotUser).where(BotUser.vk_id == user_vk_id)
        ).scalar_one_or_none()

        if user is None:
            return False

        # Проверяем, лайкнул ли нас этот профиль VK (как BotUser)
        candidate = session.execute(
            select(BotUser).where(BotUser.vk_id == profile_vk_id)
        ).scalar_one_or_none()

        if candidate is None:
            # Профиль VK не зарегистрирован в боте — мэтч невозможен
            return False

        # Проверяем, лайкнул ли candidate (как BotUser) нас
        liked_by = session.execute(
            select(UserInteraction).where(
                and_(
                    UserInteraction.user_id == candidate.id,
                    UserInteraction.profile_id == user.vk_id,
                    UserInteraction.action == 'like'
                )
            )
        ).scalar_one_or_none()

        is_match = liked_by is not None

        if is_match:
            # Создаём запись о взаимном лайке
            existing_match = session.execute(
                select(MutualLike).where(
                    and_(
                        MutualLike.user_id == user.id,
                        MutualLike.profile_id == profile_vk_id
                    )
                )
            ).scalar_one_or_none()

            if not existing_match:
                mutual = MutualLike(
                    user_id=user.id,
                    profile_id=profile_vk_id,
                    is_notified=False
                )
                session.add(mutual)

        return is_match


def get_user_interactions(
    user_vk_id: int,
    action: Optional[str] = None
) -> List[int]:
    """Получает список profile_id взаимодействий пользователя.

    Args:
        user_vk_id: vk_id пользователя.
        action: Тип действия (None = все).

    Returns:
        List[int]: Список profile_id.
    """
    with db_manager.get_session() as session:
        user = session.execute(
            select(BotUser).where(BotUser.vk_id == user_vk_id)
        ).scalar_one_or_none()

        if user is None:
            return []

        query = select(UserInteraction.profile_id).where(
            UserInteraction.user_id == user.id
        )

        if action:
            query = query.where(UserInteraction.action == action)

        results = session.execute(query).scalars().all()
        return list(results)


def add_match(user1_vk_id: int, user2_vk_id: int) -> bool:
    """Добавляет match между двумя пользователями бота.

    Args:
        user1_vk_id: vk_id первого пользователя.
        user2_vk_id: vk_id второго пользователя.

    Returns:
        bool: True если добавлено, False если дубликат.
    """
    with db_manager.get_session() as session:
        u1 = session.execute(
            select(BotUser).where(BotUser.vk_id == user1_vk_id)
        ).scalar_one_or_none()

        u2 = session.execute(
            select(BotUser).where(BotUser.vk_id == user2_vk_id)
        ).scalar_one_or_none()

        if u1 is None or u2 is None:
            return False

        # Всегда меньший vk_id — user1
        if u1.vk_id > u2.vk_id:
            u1, u2 = u2, u1

        # Проверяем дубликат по MutualLike: user_id → BotUser.id, profile_id → vk_id
        existing = session.execute(
            select(MutualLike).where(
                and_(
                    MutualLike.user_id == u1.id,
                    MutualLike.profile_id == u2.vk_id
                )
            )
        ).scalar_one_or_none()

        if existing:
            return False

        mutual = MutualLike(
            user_id=u1.id,
            profile_id=u2.vk_id,
            is_notified=False
        )
        session.add(mutual)
        return True


def remove_interaction(
    user_vk_id: int,
    profile_vk_id: int,
    action: str
) -> bool:
    """Удаляет взаимодействие из БД.

    Args:
        user_vk_id: vk_id пользователя.
        profile_vk_id: vk_id целевой анкеты.
        action: Тип действия (view, like, block).

    Returns:
        bool: True если удалено, False если не найдено.
    """
    with db_manager.get_session() as session:
        user = session.execute(
            select(BotUser).where(BotUser.vk_id == user_vk_id)
        ).scalar_one_or_none()

        if user is None:
            return False

        interaction = session.execute(
            select(UserInteraction).where(
                and_(
                    UserInteraction.user_id == user.id,
                    UserInteraction.profile_id == profile_vk_id,
                    UserInteraction.action == action
                )
            )
        ).scalar_one_or_none()

        if interaction:
            session.delete(interaction)
            return True
        return False


def get_matches(user_vk_id: int) -> List[int]:
    """Получает список vk_id матчей пользователя.

    Возвращает vk_id других пользователей бота, с которыми есть взаимный лайк.

    Args:
        user_vk_id: vk_id пользователя.

    Returns:
        List[int]: Список vk_id пользователей, с которыми есть взаимный лайк.
    """
    with db_manager.get_session() as session:
        user = session.execute(
            select(BotUser).where(BotUser.vk_id == user_vk_id)
        ).scalar_one_or_none()

        if user is None:
            return []

        # MutualLike связывает BotUser.id → vk_id профиля
        results = session.execute(
            select(MutualLike.profile_id).where(
                MutualLike.user_id == user.id
            )
        ).scalars().all()

        results2 = session.execute(
            select(MutualLike.user_id).where(
                MutualLike.profile_id == user.vk_id
            )
        ).scalars().all()

        # profile_id в MutualLike — это уже vk_id, так что возвращаем как есть
        return list(results) + list(results2)
