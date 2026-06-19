"""Модуль для создания клавиатур бота VK-Tinder-Bot.

Этот модуль содержит функции для генерации JSON-кодов клавиатур
для интерактивного взаимодействия с пользователями через VK API.
Клавиатуры включают кнопки навигации, действия и главное меню.

Пример:
    ```python
    # Создание стартовой клавиатуры
    keyboard = create_start_keyboard()
    
    # Создание клавиатуры для просмотра партнеров
    keyboard = create_partner_keyboard(current_index=0, total_count=10)
    ```
"""

import json
from typing import Optional


def create_start_keyboard() -> str:
    """Создаёт стартовую клавиатуру с кнопкой 'Начать поиск'.
    
    Возвращает JSON-строку, представляющую клавиатуру с одной
    кнопкой для начала поиска партнеров. Клавиатура не является
    единоразовой и не встроенной (inline).
    
    Returns:
        str: JSON-код клавиатуры в формате, пригодном для отправки
            через VK API.
    
    Пример:
        ```python
        # Создание стартовой клавиатуры
        keyboard_json = create_start_keyboard()
        vk.messages.send(
            user_id=123456789,
            message='Привет!',
            keyboard=keyboard_json
        )
        ```
    """
    keyboard = {
        "one_time": False,
        "inline": False,
        "buttons": [
            [{
                "action": {
                    "type": "text",
                    "payload": {"command": "start_search"},
                    "label": "Начать поиск"
                },
                "color": "positive"
            }]
        ]
    }
    return json.dumps(keyboard, ensure_ascii=False).encode('utf-8').decode('utf-8')


def create_main_menu_keyboard() -> str:
    """Создаёт клавиатуру главного меню бота.
    
    Возвращает JSON-строку с пятью кнопками:
    - 'Начать поиск' (позитивный цвет)
    - 'Список партнеров' (первичный цвет)
    - 'Список избранных' (первичный цвет)
    - 'Матчи' (позитивный цвет)
    - 'Чёрный список' (негативный цвет)
    
    Returns:
        str: JSON-код клавиатуры главного меню.
    
    Пример:
        ```python
        # Отправка сообщения с главным меню
        keyboard = create_main_menu_keyboard()
        vk.messages.send(
            user_id=123456789,
            message='Выберите действие:',
            keyboard=keyboard
        )
        ```
    """
    keyboard = {
        "one_time": False,
        "inline": False,
        "buttons": [
            [{
                "action": {
                    "type": "text",
                    "payload": {"command": "start_search"},
                    "label": "Начать поиск"
                },
                "color": "positive"
            }],
            [{
                "action": {
                    "type": "text",
                    "payload": {"command": "show_partners"},
                    "label": "Список партнёров"
                },
                "color": "primary"
            }],
            [{
                "action": {
                    "type": "text",
                    "payload": {"command": "show_favorites"},
                    "label": "Список избранных"
                },
                "color": "primary"
            }],
            [{
                "action": {
                    "type": "text",
                    "payload": {"command": "show_matches"},
                    "label": "Матчи"
                },
                "color": "positive"
            }],
            [{
                "action": {
                    "type": "text",
                    "payload": {"command": "show_blocked"},
                    "label": "Чёрный список"
                },
                "color": "negative"
            }]
        ]
    }
    return json.dumps(keyboard, ensure_ascii=False).encode('utf-8').decode('utf-8')


def create_partner_keyboard(current_index: int, total_count: int) -> str:
    """Создаёт клавиатуру для просмотра партнеров.
    
    Возвращает JSON-код клавиатуры с кнопками навигации (предыдущий/следующий),
    действиями (добавить в избранное/в черный список) и кнопкой главного меню.
    Кнопки навигации отображаются только при наличии соседних элементов.
    
    Args:
        current_index (int): Индекс текущего элемента (начинается с 0).
        total_count (int): Общее количество элементов в списке.
    
    Returns:
        str: JSON-код клавиатуры для просмотра партнеров.
    
    Пример:
        ```python
        # Создание клавиатуры для 5-го элемента из 10
        keyboard = create_partner_keyboard(current_index=4, total_count=10)
        vk.messages.send(user_id=123456789, message='...', keyboard=keyboard)
        ```
    """
    keyboard = {
        "one_time": False,
        "inline": False,
        "buttons": []
    }
    
    # Первая строка: навигация
    row1 = []
    
    if current_index > 0:
        row1.append({
            "action": {
                "type": "text",
                "payload": {"command": "previous"},
                "label": "<< Предыдущий"
            },
            "color": "secondary"
        })
    
    if current_index < total_count - 1:
        row1.append({
            "action": {
                "type": "text",
                "payload": {"command": "next"},
                "label": "Следующий >>"
            },
            "color": "secondary"
        })
    
    if row1:
        keyboard["buttons"].append(row1)
    
    # Вторая строка: действия
    keyboard["buttons"].append([
        {
            "action": {
                "type": "text",
                "payload": {"command": "add_to_favorites"},
                "label": "❤️ В избранное"
            },
            "color": "positive"
        },
        {
            "action": {
                "type": "text",
                "payload": {"command": "add_to_blocked"},
                "label": "🚫 В чёрный список"
            },
            "color": "negative"
        }
    ])
    
    # Третья строка: главное меню
    keyboard["buttons"].append([{
        "action": {
            "type": "text",
            "payload": {"command": "main_menu"},
            "label": "🏠 Главное меню"
        },
        "color": "primary"
    }])
    
    return json.dumps(keyboard, ensure_ascii=False).encode('utf-8').decode('utf-8')


def create_favorites_keyboard(current_index: int, total_count: int) -> str:
    """Создаёт клавиатуру для просмотра избранных.
    
    Возвращает JSON-код клавиатуры с кнопками навигации и действием
    удаления из избранного. Кнопки навигации отображаются только
    при наличии соседних элементов.
    
    Args:
        current_index (int): Индекс текущего элемента (начинается с 0).
        total_count (int): Общее количество элементов в списке.
    
    Returns:
        str: JSON-код клавиатуры для просмотра избранных.
    
    Пример:
        ```python
        # Создание клавиатуры для избранных
        keyboard = create_favorites_keyboard(current_index=0, total_count=5)
        vk.messages.send(user_id=123456789, message='...', keyboard=keyboard)
        ```
    """
    keyboard = {
        "one_time": False,
        "inline": False,
        "buttons": []
    }
    
    row = []
    
    if current_index > 0:
        row.append({
            "action": {
                "type": "text",
                "payload": {"command": "previous"},
                "label": "<< Предыдущий"
            },
            "color": "secondary"
        })
    
    if current_index < total_count - 1:
        row.append({
            "action": {
                "type": "text",
                "payload": {"command": "next"},
                "label": "Следующий >>"
            },
            "color": "secondary"
        })
    
    if row:
        keyboard["buttons"].append(row)
    
    keyboard["buttons"].append([{
        "action": {
            "type": "text",
            "payload": {"command": "remove_from_favorites"},
            "label": "❌ Удалить из избранного"
        },
        "color": "negative"
    }])
    
    keyboard["buttons"].append([{
        "action": {
            "type": "text",
            "payload": {"command": "main_menu"},
            "label": "🏠 Главное меню"
        },
        "color": "primary"
    }])
    
    return json.dumps(keyboard, ensure_ascii=False).encode('utf-8').decode('utf-8')


def create_blocked_keyboard(current_index: int, total_count: int) -> str:
    """Создаёт клавиатуру для просмотра чёрного списка.
    
    Возвращает JSON-код клавиатуры с кнопками навигации и действием
    удаления из черного списка. Кнопки навигации отображаются только
    при наличии соседних элементов.
    
    Args:
        current_index (int): Индекс текущего элемента (начинается с 0).
        total_count (int): Общее количество элементов в списке.
    
    Returns:
        str: JSON-код клавиатуры для просмотра черного списка.
    
    Пример:
        ```python
        # Создание клавиатуры для черного списка
        keyboard = create_blocked_keyboard(current_index=0, total_count=3)
        vk.messages.send(user_id=123456789, message='...', keyboard=keyboard)
        ```
    """
    keyboard = {
        "one_time": False,
        "inline": False,
        "buttons": []
    }
    
    row = []
    
    if current_index > 0:
        row.append({
            "action": {
                "type": "text",
                "payload": {"command": "previous"},
                "label": "<< Предыдущий"
            },
            "color": "secondary"
        })
    
    if current_index < total_count - 1:
        row.append({
            "action": {
                "type": "text",
                "payload": {"command": "next"},
                "label": "Следующий >>"
            },
            "color": "secondary"
        })
    
    if row:
        keyboard["buttons"].append(row)
    
    keyboard["buttons"].append([{
        "action": {
            "type": "text",
            "payload": {"command": "remove_from_blocked"},
            "label": "✅ Удалить из чёрного списка"
        },
        "color": "positive"
    }])
    
    keyboard["buttons"].append([{
        "action": {
            "type": "text",
            "payload": {"command": "main_menu"},
            "label": "🏠 Главное меню"
        },
        "color": "primary"
    }])
    
    return json.dumps(keyboard, ensure_ascii=False).encode('utf-8').decode('utf-8')


def create_empty_list_keyboard() -> str:
    """Создаёт клавиатуру для пустого списка.
    
    Возвращает JSON-код клавиатуры с одной кнопкой возврата
    в главное меню. Используется при отображении пустых списков
    (избранные, черный список и т.д.).
    
    Returns:
        str: JSON-код клавиатуры для пустого списка.
    
    Пример:
        ```python
        # Отображение пустого списка
        keyboard = create_empty_list_keyboard()
        vk.messages.send(user_id=123456789, message='Список пуст', keyboard=keyboard)
        ```
    """
    keyboard = {
        "one_time": False,
        "inline": False,
        "buttons": [
            [{
                "action": {
                    "type": "text",
                    "payload": {"command": "main_menu"},
                    "label": "🏠 Главное меню"
                },
                "color": "primary"
            }]
        ]
    }
    return json.dumps(keyboard, ensure_ascii=False).encode('utf-8').decode('utf-8')


def create_matches_keyboard(current_index: int, total_count: int) -> str:
    """Создаёт клавиатуру для просмотра матчей.
    
    Возвращает JSON-код клавиатуры с кнопками навигации и возврата
    в главное меню. Матчи - это пользователи с взаимным лайком.
    
    Args:
        current_index (int): Индекс текущего элемента (начинается с 0).
        total_count (int): Общее количество элементов в списке.
    
    Returns:
        str: JSON-код клавиатуры для просмотра матчей.
    
    Пример:
        ```python
        # Создание клавиатуры для матчей
        keyboard = create_matches_keyboard(current_index=0, total_count=5)
        vk.messages.send(user_id=123456789, message='Ваши матчи:', keyboard=keyboard)
        ```
    """
    keyboard = {
        "one_time": False,
        "inline": False,
        "buttons": []
    }
    
    row = []
    
    if current_index > 0:
        row.append({
            "action": {
                "type": "text",
                "payload": {"command": "previous"},
                "label": "<< Предыдущий"
            },
            "color": "secondary"
        })
    
    if current_index < total_count - 1:
        row.append({
            "action": {
                "type": "text",
                "payload": {"command": "next"},
                "label": "Следующий >>"
            },
            "color": "secondary"
        })
    
    if row:
        keyboard["buttons"].append(row)
    
    keyboard["buttons"].append([{
        "action": {
            "type": "text",
            "payload": {"command": "main_menu"},
            "label": "🏠 Главное меню"
        },
        "color": "primary"
    }])
    
    return json.dumps(keyboard, ensure_ascii=False).encode('utf-8').decode('utf-8')