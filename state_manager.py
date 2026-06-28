"""Модуль для управления состоянием пользователей."""


class UserState:
    """Класс для хранения состояния пользователя."""

    def __init__(self):
        self.users = {}

    def set_state(self, user_id, state_data):
        """Устанавливает состояние пользователя."""
        self.users[user_id] = state_data

    def get_state(self, user_id):
        """Получает состояние пользователя."""
        return self.users.get(user_id)

    def clear_state(self, user_id):
        """Очищает состояние пользователя."""
        if user_id in self.users:
            del self.users[user_id]

    def update_index(self, user_id, new_index):
        """Обновляет текущий индекс."""
        if user_id in self.users:
            self.users[user_id]["current_index"] = new_index


# Глобальный менеджер состояний
state_manager = UserState()
