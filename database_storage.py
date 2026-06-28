"""Работа с базой данных PostgreSQL."""

import logging
from datetime import date, datetime
from database.db_manager import db_manager
from database.models.user import BotUser
from database.models.profile import VKProfile
from database.models.interaction import UserInteraction
from database.models.match import Match
from sqlalchemy import and_, or_
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)


def get_or_create_user_id(user_id: int) -> int:
    """Получает или создаёт пользователя. Возвращает внутренний ID."""
    try:
        with db_manager.get_session() as session:
            user = session.query(BotUser).filter(BotUser.vk_id == user_id).first()
            if not user:
                user = BotUser(
                    vk_id=user_id,
                    name="User",
                    surname=str(user_id),
                    gender=0,
                    looking_for=2,
                    age_min=18,
                    age_max=99,
                    max_distance=50,
                    is_active=True,
                    last_active=date.today(),
                )
                session.add(user)
                session.commit()
                logger.info(f"✅ Создан новый пользователь в БД: vk_id={user_id}, internal_id={user.id}")
                return user.id
            logger.debug(f"📋 Найден существующий пользователь: vk_id={user_id}, internal_id={user.id}")
            return user.id
    except SQLAlchemyError as e:
        logger.error(f"❌ Ошибка БД при получении/создании пользователя {user_id}: {e}", exc_info=True)
        raise


def get_or_create_profile_id(vk_id: int) -> int:
    """Получает или создаёт профиль ВК. Возвращает внутренний ID."""
    try:
        with db_manager.get_session() as session:
            profile = session.query(VKProfile).filter(VKProfile.vk_id == vk_id).first()
            if not profile:
                profile = VKProfile(vk_id=vk_id)
                session.add(profile)
                session.commit()
                logger.info(f"✅ Создан новый профиль ВК в БД: vk_id={vk_id}, internal_id={profile.id}")
                return profile.id
            logger.debug(f"📋 Найден существующий профиль: vk_id={vk_id}, internal_id={profile.id}")
            return profile.id
    except SQLAlchemyError as e:
        logger.error(f"❌ Ошибка БД при получении/создании профиля {vk_id}: {e}", exc_info=True)
        raise


def add_like(user_id: int, candidate_vk_id: int) -> tuple:
    """
    Добавляет лайк кандидату.
    Возвращает кортеж: (is_match: bool, match_info: dict or None)
    """
    try:
        user_db_id = get_or_create_user_id(user_id)
        profile_db_id = get_or_create_profile_id(candidate_vk_id)

        with db_manager.get_session() as session:
            # Проверяем существование reverse_user
            reverse_user = (
                session.query(BotUser).filter(BotUser.vk_id == candidate_vk_id).first()
            )
            reverse_profile = (
                session.query(VKProfile).filter(VKProfile.vk_id == user_id).first()
            )

            is_match = False
            match_info = None

            # ✅ Проверка на None (пункт 4 из ревью)
            if reverse_user and reverse_profile:
                reverse_interaction = (
                    session.query(UserInteraction)
                    .filter(
                        and_(
                            UserInteraction.user_id == reverse_user.id,
                            UserInteraction.profile_id == profile_db_id,
                            UserInteraction.action == "like",
                        )
                    )
                    .first()
                )

                if reverse_interaction:
                    logger.info(f"🎉 Обнаружен взаимный лайк! user={user_id}, candidate={candidate_vk_id}")
                    user1_id = min(user_db_id, reverse_user.id)
                    user2_id = max(user_db_id, reverse_user.id)

                    existing_match = (
                        session.query(Match)
                        .filter(
                            and_(Match.user1_id == user1_id, Match.user2_id == user2_id)
                        )
                        .first()
                    )

                    if not existing_match:
                        match = Match(
                            user1_id=user1_id,
                            user2_id=user2_id,
                            matched_at=datetime.now(),
                            is_active=True,
                        )
                        session.add(match)
                        session.commit()
                        is_match = True
                        match_info = {
                            "match_id": match.id,
                            "user1_id": user1_id,
                            "user2_id": user2_id,
                            "other_user_vk_id": candidate_vk_id,
                        }
                        logger.info(f"✅ Создан новый мэтч: id={match.id}, между user1={user1_id} и user2={user2_id}")
                    else:
                        logger.debug(f"📋 Мэтч уже существует между {user1_id} и {user2_id}")
            else:
                logger.debug(f"⚠️ Reverse пользователь или профиль не найдены для проверки взаимности")

            # Создаем лайк (если еще не создан)
            existing = (
                session.query(UserInteraction)
                .filter(
                    and_(
                        UserInteraction.user_id == user_db_id,
                        UserInteraction.profile_id == profile_db_id,
                        UserInteraction.action == "like",
                    )
                )
                .first()
            )

            if not existing:
                interaction = UserInteraction(
                    user_id=user_db_id, profile_id=profile_db_id, action="like"
                )
                session.add(interaction)
                logger.info(f"❤️ Добавлен лайк: user={user_id} -> profile={candidate_vk_id}")
            else:
                logger.debug(f"📋 Лайк уже существует: user={user_id} -> profile={candidate_vk_id}")

            session.commit()
            return is_match, match_info

    except SQLAlchemyError as e:
        logger.error(f"❌ Ошибка БД при добавлении лайка: user={user_id}, candidate={candidate_vk_id}: {e}", exc_info=True)
        return False, None


def add_match(user_id: int, candidate_vk_id: int):
    """Заглушка — match уже создан в add_like."""
    logger.debug(f"📋 add_match вызван как заглушка для user={user_id}, candidate={candidate_vk_id}")
    pass


def add_view(user_id: int, candidate_vk_id: int):
    """Добавляет просмотр кандидата."""
    try:
        user_db_id = get_or_create_user_id(user_id)
        profile_db_id = get_or_create_profile_id(candidate_vk_id)
        with db_manager.get_session() as session:
            existing = (
                session.query(UserInteraction)
                .filter(
                    and_(
                        UserInteraction.user_id == user_db_id,
                        UserInteraction.profile_id == profile_db_id,
                        UserInteraction.action == "view",
                    )
                )
                .first()
            )
            if not existing:
                interaction = UserInteraction(
                    user_id=user_db_id, profile_id=profile_db_id, action="view"
                )
                session.add(interaction)
                session.commit()
                logger.debug(f"👁 Добавлен просмотр: user={user_id} -> profile={candidate_vk_id}")
    except SQLAlchemyError as e:
        logger.error(f"❌ Ошибка БД при добавлении просмотра: user={user_id}, candidate={candidate_vk_id}: {e}", exc_info=True)


def add_to_favorites(user_id: int, candidate_vk_id: int) -> bool:
    """
    Добавляет в избранное (сохраняет кандидата без лайка).
    Используем action="favorite" вместо "like" для разделения логики.
    """
    try:
        user_db_id = get_or_create_user_id(user_id)
        profile_db_id = get_or_create_profile_id(candidate_vk_id)

        with db_manager.get_session() as session:
            # ✅ Проверяем, что еще не добавлено (и как лайк, и как избранное)
            existing_like = (
                session.query(UserInteraction)
                .filter(
                    and_(
                        UserInteraction.user_id == user_db_id,
                        UserInteraction.profile_id == profile_db_id,
                        UserInteraction.action == "like",
                    )
                )
                .first()
            )

            existing_favorite = (
                session.query(UserInteraction)
                .filter(
                    and_(
                        UserInteraction.user_id == user_db_id,
                        UserInteraction.profile_id == profile_db_id,
                        UserInteraction.action == "favorite",
                    )
                )
                .first()
            )

            # Если уже есть лайк или избранное - ничего не делаем
            if existing_like or existing_favorite:
                logger.debug(f"⚠️ Пользователь {user_id} уже добавил {candidate_vk_id} в избранное/лайки")
                return False

            # ✅ Используем action="favorite" для избранного
            interaction = UserInteraction(
                user_id=user_db_id, profile_id=profile_db_id, action="favorite"
            )
            session.add(interaction)
            session.commit()
            logger.info(f"⭐ Добавлено в избранное: user={user_id} -> profile={candidate_vk_id}")
            return True

    except SQLAlchemyError as e:
        logger.error(f"❌ Ошибка БД при добавлении в избранное: user={user_id}, candidate={candidate_vk_id}: {e}", exc_info=True)
        return False


def add_to_blocked(user_id: int, candidate_vk_id: int) -> bool:
    """Добавляет в чёрный список."""
    try:
        user_db_id = get_or_create_user_id(user_id)
        profile_db_id = get_or_create_profile_id(candidate_vk_id)

        with db_manager.get_session() as session:
            existing = (
                session.query(UserInteraction)
                .filter(
                    and_(
                        UserInteraction.user_id == user_db_id,
                        UserInteraction.profile_id == profile_db_id,
                        UserInteraction.action == "block",
                    )
                )
                .first()
            )
            if existing:
                logger.debug(f"⚠️ Пользователь {user_id} уже заблокировал {candidate_vk_id}")
                return False
            interaction = UserInteraction(
                user_id=user_db_id, profile_id=profile_db_id, action="block"
            )
            session.add(interaction)
            session.commit()
            logger.info(f"🚫 Добавлено в чёрный список: user={user_id} -> profile={candidate_vk_id}")
            return True

    except SQLAlchemyError as e:
        logger.error(f"❌ Ошибка БД при добавлении в чёрный список: user={user_id}, candidate={candidate_vk_id}: {e}", exc_info=True)
        return False


def remove_from_favorites(user_id: int, candidate_vk_id: int) -> bool:
    """Удаляет из избранного."""
    try:
        user_db_id = get_or_create_user_id(user_id)
        profile_db_id = get_or_create_profile_id(candidate_vk_id)

        with db_manager.get_session() as session:
            # ✅ Удаляем и лайки, и избранное
            interaction = (
                session.query(UserInteraction)
                .filter(
                    and_(
                        UserInteraction.user_id == user_db_id,
                        UserInteraction.profile_id == profile_db_id,
                        UserInteraction.action.in_(["like", "favorite"]),
                    )
                )
                .first()
            )

            if interaction:
                session.delete(interaction)
                session.commit()
                logger.info(f"❌ Удалено из избранного: user={user_id} -> profile={candidate_vk_id}")
                return True
            logger.debug(f"⚠️ Пользователь {user_id} не нашёл {candidate_vk_id} в избранном")
            return False

    except SQLAlchemyError as e:
        logger.error(f"❌ Ошибка БД при удалении из избранного: user={user_id}, candidate={candidate_vk_id}: {e}", exc_info=True)
        return False


def remove_from_blocked(user_id: int, candidate_vk_id: int) -> bool:
    """Удаляет из чёрного списка."""
    try:
        user_db_id = get_or_create_user_id(user_id)
        profile_db_id = get_or_create_profile_id(candidate_vk_id)

        with db_manager.get_session() as session:
            interaction = (
                session.query(UserInteraction)
                .filter(
                    and_(
                        UserInteraction.user_id == user_db_id,
                        UserInteraction.profile_id == profile_db_id,
                        UserInteraction.action == "block",
                    )
                )
                .first()
            )
            if interaction:
                session.delete(interaction)
                session.commit()
                logger.info(f"✅ Разблокирован: user={user_id} -> profile={candidate_vk_id}")
                return True
            logger.debug(f"⚠️ Пользователь {user_id} не нашёл {candidate_vk_id} в чёрном списке")
            return False

    except SQLAlchemyError as e:
        logger.error(f"❌ Ошибка БД при удалении из чёрного списка: user={user_id}, candidate={candidate_vk_id}: {e}", exc_info=True)
        return False


def get_favorites(user_id: int) -> list:
    """Получает список избранных VK ID (и лайки, и favorites)."""
    try:
        user_db_id = get_or_create_user_id(user_id)

        with db_manager.get_session() as session:
            # ✅ Получаем и лайки, и избранное
            interactions = (
                session.query(UserInteraction)
                .filter(
                    and_(
                        UserInteraction.user_id == user_db_id,
                        UserInteraction.action.in_(["like", "favorite"]),
                    )
                )
                .all()
            )

            profile_ids = [i.profile_id for i in interactions]
            if not profile_ids:
                logger.debug(f"📭 Список избранных пуст для пользователя {user_id}")
                return []

            profiles = session.query(VKProfile).filter(VKProfile.id.in_(profile_ids)).all()
            result = [p.vk_id for p in profiles]
            logger.debug(f"📋 Получено {len(result)} избранных для пользователя {user_id}")
            return result

    except SQLAlchemyError as e:
        logger.error(f"❌ Ошибка БД при получении избранного для пользователя {user_id}: {e}", exc_info=True)
        return []


def get_blocked(user_id: int) -> list:
    """Получает чёрный список VK ID."""
    try:
        user_db_id = get_or_create_user_id(user_id)

        with db_manager.get_session() as session:
            interactions = (
                session.query(UserInteraction)
                .filter(
                    and_(
                        UserInteraction.user_id == user_db_id,
                        UserInteraction.action == "block",
                    )
                )
                .all()
            )
            profile_ids = [i.profile_id for i in interactions]
            if not profile_ids:
                logger.debug(f"📭 Чёрный список пуст для пользователя {user_id}")
                return []
            profiles = session.query(VKProfile).filter(VKProfile.id.in_(profile_ids)).all()
            result = [p.vk_id for p in profiles]
            logger.debug(f"📋 Получено {len(result)} заблокированных для пользователя {user_id}")
            return result

    except SQLAlchemyError as e:
        logger.error(f"❌ Ошибка БД при получении чёрного списка для пользователя {user_id}: {e}", exc_info=True)
        return []


def get_views(user_id: int) -> list:
    """Получает список просмотренных VK ID."""
    try:
        user_db_id = get_or_create_user_id(user_id)

        with db_manager.get_session() as session:
            interactions = (
                session.query(UserInteraction)
                .filter(
                    and_(
                        UserInteraction.user_id == user_db_id,
                        UserInteraction.action == "view",
                    )
                )
                .all()
            )
            profile_ids = [i.profile_id for i in interactions]
            if not profile_ids:
                return []
            profiles = session.query(VKProfile).filter(VKProfile.id.in_(profile_ids)).all()
            return [p.vk_id for p in profiles]

    except SQLAlchemyError as e:
        logger.error(f"❌ Ошибка БД при получении просмотров для пользователя {user_id}: {e}", exc_info=True)
        return []


def get_matches(user_id: int) -> list:
    """Получает список матчей."""
    try:
        user_db_id = get_or_create_user_id(user_id)

        with db_manager.get_session() as session:
            matches = (
                session.query(Match)
                .filter(or_(Match.user1_id == user_db_id, Match.user2_id == user_db_id))
                .all()
            )
            match_users = []
            for match in matches:
                other_user_id = (
                    match.user2_id if match.user1_id == user_db_id else match.user1_id
                )
                other_user = (
                    session.query(BotUser).filter(BotUser.id == other_user_id).first()
                )
                if other_user:
                    match_users.append(
                        {
                            "vk_id": other_user.vk_id,
                            "name": other_user.name,
                            "surname": other_user.surname,
                            "matched_at": match.matched_at,
                        }
                    )
            logger.debug(f"📋 Получено {len(match_users)} мэтчей для пользователя {user_id}")
            return match_users

    except SQLAlchemyError as e:
        logger.error(f"❌ Ошибка БД при получении мэтчей для пользователя {user_id}: {e}", exc_info=True)
        return []


def get_user_settings(user_id: int) -> dict:
    """Получает настройки поиска пользователя."""
    try:
        with db_manager.get_session() as session:
            user = session.query(BotUser).filter(BotUser.vk_id == user_id).first()
            if not user:
                logger.warning(f"⚠️ Пользователь {user_id} не найден в БД для получения настроек")
                return {}
            settings = {
                "age_min": user.age_min,
                "age_max": user.age_max,
                "max_distance": user.max_distance,
                "looking_for": user.looking_for,
                "city": user.city,
            }
            logger.debug(f"⚙️ Получены настройки пользователя {user_id}: {settings}")
            return settings

    except SQLAlchemyError as e:
        logger.error(f"❌ Ошибка БД при получении настроек пользователя {user_id}: {e}", exc_info=True)
        return {}


def update_user_settings(user_id: int, settings: dict) -> bool:
    """Обновляет настройки поиска пользователя."""
    try:
        with db_manager.get_session() as session:
            user = session.query(BotUser).filter(BotUser.vk_id == user_id).first()
            if not user:
                logger.warning(f"⚠️ Пользователь {user_id} не найден в БД для обновления настроек")
                return False
            if "age_min" in settings:
                user.age_min = settings["age_min"]
            if "age_max" in settings:
                user.age_max = settings["age_max"]
            if "max_distance" in settings:
                user.max_distance = settings["max_distance"]
            session.commit()
            logger.info(f"✅ Обновлены настройки пользователя {user_id}: {settings}")
            return True

    except SQLAlchemyError as e:
        logger.error(f"❌ Ошибка БД при обновлении настроек пользователя {user_id}: {e}", exc_info=True)
        return False