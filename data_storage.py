"""Обёртка для совместимости."""
from database_storage import (
    add_like,
    add_match,
    add_view,
    add_to_favorites,
    add_to_blocked,
    remove_from_favorites,
    remove_from_blocked,
    get_favorites,
    get_blocked,
    get_views,
    get_matches,
    get_user_settings,
    update_user_settings
)

__all__ = [
    'add_like',
    'add_match',
    'add_view',
    'add_to_favorites',
    'add_to_blocked',
    'remove_from_favorites',
    'remove_from_blocked',
    'get_favorites',
    'get_blocked',
    'get_views',
    'get_matches',
    'get_user_settings',
    'update_user_settings'
]