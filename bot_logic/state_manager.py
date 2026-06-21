"""Модуль управления состоянием пользователей VK-Tinder-Bot.

Этот модуль предоставляет класс для хранения и управления состоянием
пользователей бота, включая текущий режим работы и индекс просмотра.
Состояние сохраняется в базе данных (таблица bot_users).
"""
import json
from typing import Optional

from sqlalchemy import select
from database.db_manager import db_manager
from database.models.user import BotUser


class UserState:
    """Класс для хранения состояния пользователя в БД.
    
    Этот класс управляет состоянием пользователя, включая текущий режим работы
    (partners, favorites, blocked, matches), список кандидатов и текущий индекс.
    Состояние сохраняется в базе данных через модель BotUser.
    
    Пример:
        ```python
        from state_manager import state_manager
        
        # Установка состояния
        state_manager.set_state(user_id, {
            'mode': 'partners',
            'candidates': candidates,
            'current_index': 0
        })
        
        # Получение состояния
        state = state_manager.get_state(user_id)
        ```
    """
    
    def set_state(self, user_id: int, state_data: dict) -> None:
        """Устанавливает состояние пользователя в БД.
        
        Args:
            user_id (int): VK ID пользователя.
            state_data (dict): Словарь с данными состояния.
                Должен содержать:
                - 'mode': режим работы ('partners', 'favorites', 'blocked', 'matches', 'main_menu')
                - 'candidates' или 'favorites_list'/'blocked_list'/'matches_list': список данных
                - 'current_index': текущий индекс просмотра
                - 'user_info': данные пользователя (опционально)
        
        Пример:
            ```python
            state_manager.set_state(123456, {
                'mode': 'partners',
                'candidates': candidates_list,
                'current_index': 0
            })
            ```
        """
        with db_manager.get_session() as session:
            user = session.execute(
                select(BotUser).where(BotUser.vk_id == user_id)
            ).scalar_one_or_none()

            if user is None:
                return

            user.state_mode = state_data.get('mode', 'main_menu')
            user.state_current_index = state_data.get('current_index', 0)
            
            # Сериализуем списки в JSON-строки
            if 'candidates' in state_data:
                user.state_candidates = json.dumps(state_data['candidates'], ensure_ascii=False)
            if 'favorites_list' in state_data:
                user.state_favorites_list = json.dumps(state_data['favorites_list'], ensure_ascii=False)
            if 'blocked_list' in state_data:
                user.state_blocked_list = json.dumps(state_data['blocked_list'], ensure_ascii=False)
            if 'matches_list' in state_data:
                user.state_matches_list = json.dumps(state_data['matches_list'], ensure_ascii=False)
            if 'user_info' in state_data:
                user.state_user_info = json.dumps(state_data['user_info'], ensure_ascii=False)

    def get_state(self, user_id: int) -> Optional[dict]:
        """Получает состояние пользователя из БД.
        
        Args:
            user_id (int): VK ID пользователя.
        
        Returns:
            Optional[dict]: Словарь с данными состояния или None, если состояние
                не найдено.
        
        Пример:
            ```python
            state = state_manager.get_state(123456)
            if state:
                print(f"Текущий режим: {state['mode']}")
            ```
        """
        with db_manager.get_session() as session:
            user = session.execute(
                select(BotUser).where(BotUser.vk_id == user_id)
            ).scalar_one_or_none()

            if user is None:
                return None

            return {
                'mode': user.state_mode,
                'current_index': user.state_current_index,
                'candidates': json.loads(user.state_candidates) if user.state_candidates else [],
                'favorites_list': json.loads(user.state_favorites_list) if user.state_favorites_list else [],
                'blocked_list': json.loads(user.state_blocked_list) if user.state_blocked_list else [],
                'matches_list': json.loads(user.state_matches_list) if user.state_matches_list else [],
                'user_info': json.loads(user.state_user_info) if user.state_user_info else None,
            }
    
    def clear_state(self, user_id: int) -> None:
        """Очищает состояние пользователя в БД.
        
        Args:
            user_id (int): VK ID пользователя.
        
        Пример:
            ```python
            state_manager.clear_state(123456)
            ```
        """
        with db_manager.get_session() as session:
            user = session.execute(
                select(BotUser).where(BotUser.vk_id == user_id)
            ).scalar_one_or_none()

            if user is None:
                return

            # Сбрасываем все поля состояния
            user.state_mode = 'main_menu'
            user.state_current_index = 0
            user.state_candidates = None
            user.state_favorites_list = None
            user.state_blocked_list = None
            user.state_matches_list = None
            user.state_user_info = None

    def update_index(self, user_id: int, new_index: int) -> None:
        """Обновляет текущий индекс пользователя в БД.
        
        Args:
            user_id (int): VK ID пользователя.
            new_index (int): Новый индекс для установки.
        
        Пример:
            ```python
            # Перейти к следующему элементу
            state_manager.update_index(123456, current_index + 1)
            ```
        """
        with db_manager.get_session() as session:
            user = session.execute(
                select(BotUser).where(BotUser.vk_id == user_id)
            ).scalar_one_or_none()

            if user is None:
                return

            user.state_current_index = new_index


# Глобальный менеджер состояний
state_manager = UserState()
