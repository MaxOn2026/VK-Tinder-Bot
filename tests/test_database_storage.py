"""Тесты для модуля database_storage."""
import pytest
from datetime import date
from database.models.user import BotUser
from database.models.profile import VKProfile
from database.models.interaction import UserInteraction
from database.models.match import Match


class TestBotUser:
    """Тесты для модели BotUser."""

    def test_create_user(self, test_session):
        """Тест создания пользователя."""
        user = BotUser(
            vk_id=123456,
            name="Иван",
            surname="Петров",
            gender=2,
            looking_for=1,
            city="Москва",
            age_min=20,
            age_max=30,
            max_distance=50,
            is_active=True,
            last_active=date.today()
        )
        test_session.add(user)
        test_session.commit()

        # Проверяем, что пользователь создан
        saved_user = test_session.query(BotUser).filter_by(vk_id=123456).first()
        assert saved_user is not None
        assert saved_user.name == "Иван"
        assert saved_user.surname == "Петров"
        assert saved_user.gender == 2
        assert saved_user.age_min == 20
        assert saved_user.age_max == 30

    def test_user_full_name(self, test_session):
        """Тест свойства full_name."""
        user = BotUser(
            vk_id=123456,
            name="Иван",
            surname="Петров"
        )
        test_session.add(user)
        test_session.commit()

        assert user.full_name == "Иван Петров"

    def test_user_age(self, test_session):
        """Тест вычисления возраста."""
        from datetime import date
        user = BotUser(
            vk_id=123456,
            name="Иван",
            surname="Петров",
            birthdate=date(2000, 1, 1)
        )
        test_session.add(user)
        test_session.commit()

        # Возраст должен быть примерно 26 лет (в 2026 году)
        assert user.age == 26

    def test_user_age_none(self, test_session):
        """Тест возраста без даты рождения."""
        user = BotUser(
            vk_id=123456,
            name="Иван",
            surname="Петров"
        )
        test_session.add(user)
        test_session.commit()

        assert user.age is None

    def test_unique_vk_id(self, test_session):
        """Тест уникальности vk_id."""
        user1 = BotUser(vk_id=123456, name="Иван", surname="Петров")
        user2 = BotUser(vk_id=123456, name="Пётр", surname="Иванов")

        test_session.add(user1)
        test_session.commit()

        test_session.add(user2)
        with pytest.raises(Exception):  # IntegrityError
            test_session.commit()


class TestVKProfile:
    """Тесты для модели VKProfile."""

    def test_create_profile(self, test_session):
        """Тест создания профиля."""
        profile = VKProfile(
            vk_id=789012,
            first_name="Анна",
            last_name="Сидорова",
            birth_year=1995,
            gender=1,
            city="Москва"
        )
        test_session.add(profile)
        test_session.commit()

        saved_profile = test_session.query(VKProfile).filter_by(vk_id=789012).first()
        assert saved_profile is not None
        assert saved_profile.first_name == "Анна"
        assert saved_profile.gender == 1

    def test_profile_full_name(self, test_session):
        """Тест свойства full_name для профиля."""
        profile = VKProfile(
            vk_id=789012,
            first_name="Анна",
            last_name="Сидорова"
        )
        test_session.add(profile)
        test_session.commit()

        assert profile.full_name == "Анна Сидорова"


class TestUserInteraction:
    """Тесты для модели UserInteraction."""

    def test_create_interaction(self, test_session):
        """Тест создания взаимодействия."""
        user = BotUser(vk_id=123456, name="Иван", surname="Петров")
        profile = VKProfile(vk_id=789012, first_name="Анна", last_name="Сидорова")
        test_session.add_all([user, profile])
        test_session.commit()

        interaction = UserInteraction(
            user_id=user.id,
            profile_id=profile.id,
            action="like"
        )
        test_session.add(interaction)
        test_session.commit()

        saved = test_session.query(UserInteraction).first()
        assert saved is not None
        assert saved.action == "like"
        assert saved.user_id == user.id
        assert saved.profile_id == profile.id

    def test_interaction_actions(self, test_session):
        """Тест разных типов действий."""
        user = BotUser(vk_id=123456, name="Иван", surname="Петров")
        profile = VKProfile(vk_id=789012, first_name="Анна", last_name="Сидорова")
        test_session.add_all([user, profile])
        test_session.commit()

        actions = ["view", "like", "block"]
        for action in actions:
            interaction = UserInteraction(
                user_id=user.id,
                profile_id=profile.id,
                action=action
            )
            test_session.add(interaction)
            test_session.commit()

        interactions = test_session.query(UserInteraction).all()
        assert len(interactions) == 3


class TestMatch:
    """Тесты для модели Match."""

    def test_create_match(self, test_session):
        """Тест создания мэтча."""
        user1 = BotUser(vk_id=123456, name="Иван", surname="Петров")
        user2 = BotUser(vk_id=789012, name="Анна", surname="Сидорова")
        test_session.add_all([user1, user2])
        test_session.commit()

        match = Match(
            user1_id=min(user1.id, user2.id),
            user2_id=max(user1.id, user2.id),
            is_active=True
        )
        test_session.add(match)
        test_session.commit()

        saved = test_session.query(Match).first()
        assert saved is not None
        assert saved.user1_id < saved.user2_id
        assert saved.is_active is True

    def test_match_users_order(self, test_session):
        """Тест что user1_id всегда меньше user2_id."""
        user1 = BotUser(vk_id=123456, name="Иван", surname="Петров")
        user2 = BotUser(vk_id=789012, name="Анна", surname="Сидорова")
        test_session.add_all([user1, user2])
        test_session.commit()

        # Пытаемся создать мэтч с неправильным порядком
        match = Match(
            user1_id=max(user1.id, user2.id),  # Нарушение правила
            user2_id=min(user1.id, user2.id),
            is_active=True
        )
        test_session.add(match)
        with pytest.raises(Exception):  # CheckConstraint violation
            test_session.commit()


class TestRelationships:
    """Тесты связей между моделями."""

    def test_user_interactions_relationship(self, test_session):
        """Тест связи User -> Interactions."""
        user = BotUser(vk_id=123456, name="Иван", surname="Петров")
        profile = VKProfile(vk_id=789012, first_name="Анна", last_name="Сидорова")
        test_session.add_all([user, profile])
        test_session.commit()

        interaction = UserInteraction(
            user_id=user.id,
            profile_id=profile.id,
            action="like"
        )
        test_session.add(interaction)
        test_session.commit()

        # Проверяем связь
        assert len(user.interactions.all()) == 1
        assert user.interactions.first().action == "like"

    def test_match_users_relationship(self, test_session):
        """Тест связи Match -> Users."""
        user1 = BotUser(vk_id=123456, name="Иван", surname="Петров")
        user2 = BotUser(vk_id=789012, name="Анна", surname="Сидорова")
        test_session.add_all([user1, user2])
        test_session.commit()

        match = Match(
            user1_id=user1.id,
            user2_id=user2.id,
            is_active=True
        )
        test_session.add(match)
        test_session.commit()

        # Проверяем связи
        assert match.user1.full_name == "Иван Петров"
        assert match.user2.full_name == "Анна Сидорова"
        assert len(user1.matches_as_user1) == 1
        assert len(user2.matches_as_user2) == 1