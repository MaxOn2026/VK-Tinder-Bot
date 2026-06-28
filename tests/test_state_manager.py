"""Тесты для модуля state_manager."""
import pytest
from state_manager import UserState


class TestUserState:
    """Тесты для класса UserState."""

    def test_set_and_get_state(self):
        """Тест установки и получения состояния."""
        state_manager = UserState()
        user_id = 123456
        
        state_manager.set_state(user_id, {
            'mode': 'partners',
            'candidates': [1, 2, 3],
            'current_index': 0
        })
        
        state = state_manager.get_state(user_id)
        assert state is not None
        assert state['mode'] == 'partners'
        assert state['candidates'] == [1, 2, 3]
        assert state['current_index'] == 0

    def test_get_nonexistent_state(self):
        """Тест получения состояния несуществующего пользователя."""
        state_manager = UserState()
        state = state_manager.get_state(999999)
        assert state is None

    def test_update_index(self):
        """Тест обновления индекса."""
        state_manager = UserState()
        user_id = 123456
        
        state_manager.set_state(user_id, {
            'mode': 'partners',
            'candidates': [1, 2, 3],
            'current_index': 0
        })
        
        state_manager.update_index(user_id, 1)
        state = state_manager.get_state(user_id)
        assert state['current_index'] == 1

    def test_clear_state(self):
        """Тест очистки состояния."""
        state_manager = UserState()
        user_id = 123456
        
        state_manager.set_state(user_id, {'mode': 'test'})
        state_manager.clear_state(user_id)
        
        state = state_manager.get_state(user_id)
        assert state is None

    def test_multiple_users(self):
        """Тест работы с несколькими пользователями."""
        state_manager = UserState()
        
        state_manager.set_state(111, {'mode': 'user1'})
        state_manager.set_state(222, {'mode': 'user2'})
        
        assert state_manager.get_state(111)['mode'] == 'user1'
        assert state_manager.get_state(222)['mode'] == 'user2'