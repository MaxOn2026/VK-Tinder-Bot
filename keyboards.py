"""Модуль для создания клавиатур бота."""
import json


def create_start_keyboard():
    """Создаёт стартовую клавиатуру с кнопкой 'Начать поиск'."""
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


def create_main_menu_keyboard():
    """Создаёт клавиатуру главного меню."""
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
            },
            {
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


def create_partner_keyboard(current_index, total_count):
    """Создаёт клавиатуру для просмотра партнёров."""
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


def create_favorites_keyboard(current_index, total_count):
    """Создаёт клавиатуру для просмотра избранного."""
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


def create_blocked_keyboard(current_index, total_count):
    """Создаёт клавиатуру для просмотра чёрного списка."""
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


def create_empty_list_keyboard():
    """Создаёт клавиатуру для пустого списка."""
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