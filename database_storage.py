"""Работа с базой данных PostgreSQL."""
from datetime import date, datetime
from database.db_manager import db_manager
from database.models.user import BotUser
from database.models.profile import VKProfile
from database.models.interaction import UserInteraction
from database.models.match import Match
from sqlalchemy import and_, or_


def get_or_create_user_id(user_id: int) -> int:
    """Получает или создаёт пользователя. Возвращает внутренний ID."""
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
                last_active=date.today()
            )
            session.add(user)
            session.commit()
            user_id_internal = user.id
        else:
            user_id_internal = user.id
        
        return user_id_internal


def get_or_create_profile_id(vk_id: int) -> int:
    """Получает или создаёт профиль ВК. Возвращает внутренний ID."""
    with db_manager.get_session() as session:
        profile = session.query(VKProfile).filter(VKProfile.vk_id == vk_id).first()
        
        if not profile:
            profile = VKProfile(vk_id=vk_id)
            session.add(profile)
            session.commit()
            profile_id = profile.id
        else:
            profile_id = profile.id
        
        return profile_id


def add_like(user_id: int, candidate_vk_id: int) -> bool:
    """Добавляет лайк. Возвращает True, если это match."""
    user_db_id = get_or_create_user_id(user_id)
    profile_db_id = get_or_create_profile_id(candidate_vk_id)
    
    with db_manager.get_session() as session:
        # Проверяем, лайкнул ли этот профиль текущего пользователя
        reverse_user = session.query(BotUser).filter(BotUser.vk_id == candidate_vk_id).first()
        reverse_profile = session.query(VKProfile).filter(VKProfile.vk_id == user_id).first()
        
        is_match = False
        
        if reverse_user and reverse_profile:
            reverse_interaction = session.query(UserInteraction).filter(
                and_(
                    UserInteraction.user_id == reverse_user.id,
                    UserInteraction.profile_id == reverse_profile.id,
                    UserInteraction.action == "like"
                )
            ).first()
            
            if reverse_interaction:
                # Создаём match
                user1_id = min(user_db_id, reverse_user.id)
                user2_id = max(user_db_id, reverse_user.id)
                
                existing_match = session.query(Match).filter(
                    and_(
                        Match.user1_id == user1_id,
                        Match.user2_id == user2_id
                    )
                ).first()
                
                if not existing_match:
                    match = Match(
                        user1_id=user1_id,
                        user2_id=user2_id,
                        matched_at=datetime.now(),
                        is_active=True
                    )
                    session.add(match)
                    is_match = True
        
        # Добавляем лайк
        existing = session.query(UserInteraction).filter(
            and_(
                UserInteraction.user_id == user_db_id,
                UserInteraction.profile_id == profile_db_id,
                UserInteraction.action == "like"
            )
        ).first()
        
        if not existing:
            interaction = UserInteraction(
                user_id=user_db_id,
                profile_id=profile_db_id,
                action="like"
            )
            session.add(interaction)
        
        session.commit()
        return is_match


def add_match(user_id: int, candidate_vk_id: int):
    """Создаёт match (если ещё не создан)."""
    # Match уже создан в add_like, так что ничего не делаем
    pass


def add_view(user_id: int, candidate_vk_id: int):
    """Добавляет просмотр кандидата."""
    user_db_id = get_or_create_user_id(user_id)
    profile_db_id = get_or_create_profile_id(candidate_vk_id)
    
    with db_manager.get_session() as session:
        existing = session.query(UserInteraction).filter(
            and_(
                UserInteraction.user_id == user_db_id,
                UserInteraction.profile_id == profile_db_id,
                UserInteraction.action == "view"
            )
        ).first()
        
        if not existing:
            interaction = UserInteraction(
                user_id=user_db_id,
                profile_id=profile_db_id,
                action="view"
            )
            session.add(interaction)
            session.commit()


def add_to_favorites(user_id: int, candidate_vk_id: int) -> bool:
    """Добавляет в избранное. Возвращает True, если добавлено."""
    user_db_id = get_or_create_user_id(user_id)
    profile_db_id = get_or_create_profile_id(candidate_vk_id)
    
    with db_manager.get_session() as session:
        existing = session.query(UserInteraction).filter(
            and_(
                UserInteraction.user_id == user_db_id,
                UserInteraction.profile_id == profile_db_id,
                UserInteraction.action == "like"
            )
        ).first()
        
        if existing:
            return False
        
        interaction = UserInteraction(
            user_id=user_db_id,
            profile_id=profile_db_id,
            action="like"
        )
        session.add(interaction)
        session.commit()
        return True


def add_to_blocked(user_id: int, candidate_vk_id: int) -> bool:
    """Добавляет в чёрный список. Возвращает True, если добавлено."""
    user_db_id = get_or_create_user_id(user_id)
    profile_db_id = get_or_create_profile_id(candidate_vk_id)
    
    with db_manager.get_session() as session:
        existing = session.query(UserInteraction).filter(
            and_(
                UserInteraction.user_id == user_db_id,
                UserInteraction.profile_id == profile_db_id,
                UserInteraction.action == "block"
            )
        ).first()
        
        if existing:
            return False
        
        interaction = UserInteraction(
            user_id=user_db_id,
            profile_id=profile_db_id,
            action="block"
        )
        session.add(interaction)
        session.commit()
        return True


def remove_from_favorites(user_id: int, candidate_vk_id: int) -> bool:
    """Удаляет из избранного. Возвращает True, если удалено."""
    user_db_id = get_or_create_user_id(user_id)
    profile_db_id = get_or_create_profile_id(candidate_vk_id)
    
    with db_manager.get_session() as session:
        interaction = session.query(UserInteraction).filter(
            and_(
                UserInteraction.user_id == user_db_id,
                UserInteraction.profile_id == profile_db_id,
                UserInteraction.action == "like"
            )
        ).first()
        
        if interaction:
            session.delete(interaction)
            session.commit()
            return True
        
        return False


def remove_from_blocked(user_id: int, candidate_vk_id: int) -> bool:
    """Удаляет из чёрного списка. Возвращает True, если удалено."""
    user_db_id = get_or_create_user_id(user_id)
    profile_db_id = get_or_create_profile_id(candidate_vk_id)
    
    with db_manager.get_session() as session:
        interaction = session.query(UserInteraction).filter(
            and_(
                UserInteraction.user_id == user_db_id,
                UserInteraction.profile_id == profile_db_id,
                UserInteraction.action == "block"
            )
        ).first()
        
        if interaction:
            session.delete(interaction)
            session.commit()
            return True
        
        return False


def get_favorites(user_id: int) -> list:
    """Получает список избранных VK ID."""
    user_db_id = get_or_create_user_id(user_id)
    
    with db_manager.get_session() as session:
        interactions = session.query(UserInteraction).filter(
            and_(
                UserInteraction.user_id == user_db_id,
                UserInteraction.action == "like"
            )
        ).all()
        
        profile_ids = [i.profile_id for i in interactions]
        
        if not profile_ids:
            return []
        
        profiles = session.query(VKProfile).filter(
            VKProfile.id.in_(profile_ids)
        ).all()
        
        return [p.vk_id for p in profiles]


def get_blocked(user_id: int) -> list:
    """Получает чёрный список VK ID."""
    user_db_id = get_or_create_user_id(user_id)
    
    with db_manager.get_session() as session:
        interactions = session.query(UserInteraction).filter(
            and_(
                UserInteraction.user_id == user_db_id,
                UserInteraction.action == "block"
            )
        ).all()
        
        profile_ids = [i.profile_id for i in interactions]
        
        if not profile_ids:
            return []
        
        profiles = session.query(VKProfile).filter(
            VKProfile.id.in_(profile_ids)
        ).all()
        
        return [p.vk_id for p in profiles]


def get_views(user_id: int) -> list:
    """Получает список просмотренных VK ID."""
    user_db_id = get_or_create_user_id(user_id)
    
    with db_manager.get_session() as session:
        interactions = session.query(UserInteraction).filter(
            and_(
                UserInteraction.user_id == user_db_id,
                UserInteraction.action == "view"
            )
        ).all()
        
        profile_ids = [i.profile_id for i in interactions]
        
        if not profile_ids:
            return []
        
        profiles = session.query(VKProfile).filter(
            VKProfile.id.in_(profile_ids)
        ).all()
        
        return [p.vk_id for p in profiles]


def get_matches(user_id: int) -> list:
    """Получает список матчей."""
    user_db_id = get_or_create_user_id(user_id)
    
    with db_manager.get_session() as session:
        matches = session.query(Match).filter(
            or_(
                Match.user1_id == user_db_id,
                Match.user2_id == user_db_id
            )
        ).all()
        
        match_users = []
        for match in matches:
            other_user_id = match.user2_id if match.user1_id == user_db_id else match.user1_id
            other_user = session.query(BotUser).filter(BotUser.id == other_user_id).first()
            if other_user:
                match_users.append({
                    "vk_id": other_user.vk_id,
                    "name": other_user.name,
                    "surname": other_user.surname,
                    "matched_at": match.matched_at
                })
        
        return match_users