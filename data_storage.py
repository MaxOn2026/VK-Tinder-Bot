"""Модуль для сохранения данных в JSON файл."""
import json
import os
from pathlib import Path


DATA_FILE = "user_data.json"


def load_all_data():
    """Загружает все данные из файла."""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def save_all_data(data):
    """Сохраняет все данные в файл."""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_user_data(user_id):
    """Получает данные пользователя."""
    all_data = load_all_data()
    return all_data.get(str(user_id), {
        'favorites': [],
        'blocked': [],
        'matches': [],
        'views': [],
        'likes_sent': [],
        'likes_received': []
    })


def save_user_data(user_id, user_data):
    """Сохраняет данные пользователя."""
    all_data = load_all_data()
    all_data[str(user_id)] = user_data
    save_all_data(all_data)


def add_to_favorites(user_id, candidate_id):
    """Добавляет в избранное."""
    user_data = get_user_data(user_id)
    if candidate_id not in user_data['favorites']:
        user_data['favorites'].append(candidate_id)
        save_user_data(user_id, user_data)
        return True
    return False


def add_to_blocked(user_id, candidate_id):
    """Добавляет в чёрный список."""
    user_data = get_user_data(user_id)
    if candidate_id not in user_data['blocked']:
        user_data['blocked'].append(candidate_id)
        save_user_data(user_id, user_data)
        return True
    return False


def remove_from_favorites(user_id, candidate_id):
    """Удаляет из избранного."""
    user_data = get_user_data(user_id)
    if candidate_id in user_data['favorites']:
        user_data['favorites'].remove(candidate_id)
        save_user_data(user_id, user_data)
        return True
    return False


def remove_from_blocked(user_id, candidate_id):
    """Удаляет из чёрного списка."""
    user_data = get_user_data(user_id)
    if candidate_id in user_data['blocked']:
        user_data['blocked'].remove(candidate_id)
        save_user_data(user_id, user_data)
        return True
    return False


def add_like(user_id, candidate_id):
    """Добавляет лайк и проверяет match."""
    user_data = get_user_data(user_id)
    
    # Проверяем, лайкнул ли нас этот пользователь
    candidate_data = get_user_data(candidate_id)
    
    is_match = user_id in candidate_data.get('likes_received', [])
    
    # Сохраняем лайк
    if 'likes_sent' not in user_data:
        user_data['likes_sent'] = []
    user_data['likes_sent'].append(candidate_id)
    
    # Сохраняем полученный лайк у кандидата
    if 'likes_received' not in candidate_data:
        candidate_data['likes_received'] = []
    candidate_data['likes_received'].append(user_id)
    
    save_user_data(user_id, user_data)
    save_user_data(candidate_id, candidate_data)
    
    return is_match


def add_match(user_id, candidate_id):
    """Добавляет match."""
    user_data = get_user_data(user_id)
    if candidate_id not in user_data['matches']:
        user_data['matches'].append(candidate_id)
        save_user_data(user_id, user_data)
    
    candidate_data = get_user_data(candidate_id)
    if user_id not in candidate_data['matches']:
        candidate_data['matches'].append(user_id)
        save_user_data(candidate_id, candidate_data)


def get_favorites(user_id):
    """Получает список избранных."""
    user_data = get_user_data(user_id)
    return user_data.get('favorites', [])


def get_blocked(user_id):
    """Получает чёрный список."""
    user_data = get_user_data(user_id)
    return user_data.get('blocked', [])


def get_matches(user_id):
    """Получает список matches."""
    user_data = get_user_data(user_id)
    return user_data.get('matches', [])


def add_view(user_id, candidate_id):
    """Добавляет просмотр."""
    user_data = get_user_data(user_id)
    if 'views' not in user_data:
        user_data['views'] = []
    if candidate_id not in user_data['views']:
        user_data['views'].append(candidate_id)
        save_user_data(user_id, user_data)


def get_views(user_id):
    """Получает список просмотренных кандидатов."""
    user_data = get_user_data(user_id)
    return user_data.get('views', [])