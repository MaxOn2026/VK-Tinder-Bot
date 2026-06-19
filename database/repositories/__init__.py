"""Репозитории для работы с базой данных."""
from database.repositories.user_repo import get_or_create_user, get_user, update_user_preferences
from database.repositories.interaction_repo import (
    add_interaction,
    add_like_and_check_match,
    get_user_interactions,
    add_match,
    remove_interaction,
    get_matches,
)

__all__ = [
    "get_or_create_user",
    "get_user",
    "update_user_preferences",
    "add_interaction",
    "add_like_and_check_match",
    "get_user_interactions",
    "add_match",
    "remove_interaction",
    "get_matches",
]
