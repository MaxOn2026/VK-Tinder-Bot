"""Тесты для модуля handlers."""
import pytest
from unittest.mock import Mock, patch, MagicMock


class TestSendCommand:
    """Тесты команд бота."""

    @patch('handlers.get_vk_session')
    def test_send_message_success(self, mock_get_session):
        """Тест успешной отправки сообщения."""
        from handlers import send_message
        
        mock_vk = Mock()
        mock_api = Mock()
        mock_get_session.return_value = mock_vk
        mock_vk.get_api.return_value = mock_api
        mock_api.messages.send.return_value = None
        
        result = send_message(123456, "Тестовое сообщение")
        
        assert result is True
        mock_api.messages.send.assert_called_once()

    @patch('handlers.get_vk_session')
    def test_send_message_with_keyboard(self, mock_get_session):
        """Тест отправки сообщения с клавиатурой."""
        from handlers import send_message
        
        mock_vk = Mock()
        mock_api = Mock()
        mock_get_session.return_value = mock_vk
        mock_vk.get_api.return_value = mock_api
        
        result = send_message(
            123456, 
            "Тест", 
            keyboard='{"buttons": []}'
        )
        
        assert result is True
        call_args = mock_api.messages.send.call_args[1]
        assert 'keyboard' in call_args

    @patch('handlers.get_vk_session')
    def test_send_message_with_attachment(self, mock_get_session):
        """Тест отправки сообщения с вложением."""
        from handlers import send_message
        
        mock_vk = Mock()
        mock_api = Mock()
        mock_get_session.return_value = mock_vk
        mock_vk.get_api.return_value = mock_api
        
        result = send_message(
            123456, 
            "Тест", 
            attachment="photo123_456"
        )
        
        assert result is True
        call_args = mock_api.messages.send.call_args[1]
        assert call_args['attachment'] == "photo123_456"


class TestCommandRouting:
    """Тесты роутинга команд."""

    def test_command_routes_exist(self):
        """Тест что словарь команд существует."""
        from bot import COMMAND_ROUTES
        assert isinstance(COMMAND_ROUTES, dict)
        assert len(COMMAND_ROUTES) > 0

    def test_main_commands_in_routes(self):
        """Тест основных команд в словаре."""
        from bot import COMMAND_ROUTES
        
        main_commands = [
            'начать', 'start', 'поиск',
            'следующий', 'далее',
            'предыдущий', 'назад',
            'в избранное', 'лайк',
            'в чс', 'чёрный список',
            'меню', 'главное меню'
        ]
        
        for cmd in main_commands:
            assert cmd in COMMAND_ROUTES, f"Команда '{cmd}' не найдена в COMMAND_ROUTES"