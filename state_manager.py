"""Модуль управления состоянием пользователей VK-Tinder-Bot.

Этот модуль предоставляет класс для хранения и управления состоянием
пользователей бота, включая текущий режим работы и индекс просмотра.
"""

class UserState:
    """Класс для хранения состояния пользователя.
    
    Этот класс управляет состоянием пользователя, включая текущий режим работы
    (partners, favorites, blocked, matches), список кандидатов и текущий индекс.
    
    Атрибуты:
        users (dict): Словарь, где ключ - vk_id пользователя, а значение -
            словарь с состоянием пользователя.
    
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
    
    def __init__(self):
        """Инициализирует пустой словарь для хранения состояний пользователей."""
        self.users = {}
    
    def set_state(self, user_id: int, state_data: dict) -> None:
        """Устанавливает состояние пользователя.
        
        Args:
            user_id (int): VK ID пользователя.
            state_data (dict): Словарь с данными состояния.
                Должен содержать:
                - 'mode': режим работы ('partners', 'favorites', 'blocked', 'matches')
                - 'candidates' или 'favorites_list'/'blocked_list'/'matches_list': список данных
                - 'current_index': текущий индекс просмотра
        
        Пример:
            ```python
            state_manager.set_state(123456, {
                'mode': 'partners',
                'candidates': candidates_list,
                'current_index': 0
            })
            ```
        """
        self.users[user_id] = state_data
    
    def get_state(self, user_id: int) -> dict | None:
        """Получает состояние пользователя.
        
        Args:
            user_id (int): VK ID пользователя.
        
        Returns:
            dict | None: Словарь с данными состояния или None, если состояние
                не найдено.
        
        Пример:
            ```python
            state = state_manager.get_state(123456)
            if state:
                print(f"Текущий режим: {state['mode']}")
            ```
        """
        return self.users.get(user_id)
    
    def clear_state(self, user_id: int) -> None:
        """Очищает состояние пользователя.
        
        Args:
            user_id (int): VK ID пользователя.
        
        Пример:
            ```python
            state_manager.clear_state(123456)
            ```
        """
        if user_id in self.users:
            del self.users[user_id]
    
    def update_index(self, user_id: int, new_index: int) -> None:
        """Обновляет текущий индекс пользователя.
        
        Args:
            user_id (int): VK ID пользователя.
            new_index (int): Новый индекс для установки.
        
        Пример:
            ```python
            # Перейти к следующему элементу
            state_manager.update_index(123456, current_index + 1)
            ```
        """
        if user_id in self.users:
            self.users[user_id]['current_index'] = new_index


# Глобальный менеджер состояний
state_manager = UserState()
