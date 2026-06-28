"""Модуль клавиатур для бота."""

from vk_api.keyboard import VkKeyboard, VkKeyboardColor


def create_start_keyboard():
    """Создаёт клавиатуру для начала работы."""
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_button("🔍 Начать поиск", color=VkKeyboardColor.POSITIVE)
    keyboard.add_line()
    keyboard.add_button("📊 Статистика", color=VkKeyboardColor.PRIMARY)
    return keyboard.get_keyboard()


def create_main_menu_keyboard():
    """Создаёт клавиатуру главного меню."""
    keyboard = VkKeyboard(one_time=False)

    keyboard.add_button("🔍 Начать поиск", color=VkKeyboardColor.POSITIVE)
    keyboard.add_button("📊 Статистика", color=VkKeyboardColor.PRIMARY)

    keyboard.add_line()
    keyboard.add_button("❤️ Избранное", color=VkKeyboardColor.POSITIVE)
    keyboard.add_button("🚫 Чёрный список", color=VkKeyboardColor.NEGATIVE)

    keyboard.add_line()
    keyboard.add_button("🎉 Мэтчи", color=VkKeyboardColor.POSITIVE)
    keyboard.add_button("⚙️ Настройки", color=VkKeyboardColor.PRIMARY)

    keyboard.add_line()
    keyboard.add_button("🔐 Админ-панель", color=VkKeyboardColor.SECONDARY)

    return keyboard.get_keyboard()


def create_partner_keyboard(current_index, total):
    """Создаёт клавиатуру для просмотра кандидата."""
    keyboard = VkKeyboard(one_time=False)

    keyboard.add_button("❤️ В избранное", color=VkKeyboardColor.POSITIVE)
    keyboard.add_button("🚫 В ЧС", color=VkKeyboardColor.NEGATIVE)

    keyboard.add_line()
    keyboard.add_button("<< Назад", color=VkKeyboardColor.SECONDARY)
    keyboard.add_button("Далее >>", color=VkKeyboardColor.SECONDARY)

    keyboard.add_line()
    keyboard.add_button("🏠 Главное меню", color=VkKeyboardColor.PRIMARY)

    return keyboard.get_keyboard()


def create_favorites_keyboard(current_index, total):
    """Создаёт клавиатуру для списка избранных."""
    keyboard = VkKeyboard(one_time=False)

    keyboard.add_button("❌ Удалить", color=VkKeyboardColor.NEGATIVE)

    keyboard.add_line()
    keyboard.add_button("<< Назад", color=VkKeyboardColor.SECONDARY)
    keyboard.add_button("Далее >>", color=VkKeyboardColor.SECONDARY)

    keyboard.add_line()
    keyboard.add_button(" Главное меню", color=VkKeyboardColor.PRIMARY)

    return keyboard.get_keyboard()


def create_blocked_keyboard(current_index, total):
    """Создаёт клавиатуру для чёрного списка."""
    keyboard = VkKeyboard(one_time=False)

    keyboard.add_button("✅ Разблокировать", color=VkKeyboardColor.POSITIVE)

    keyboard.add_line()
    keyboard.add_button("<< Назад", color=VkKeyboardColor.SECONDARY)
    keyboard.add_button("Далее >>", color=VkKeyboardColor.SECONDARY)

    keyboard.add_line()
    keyboard.add_button("🏠 Главное меню", color=VkKeyboardColor.PRIMARY)

    return keyboard.get_keyboard()


def create_empty_list_keyboard():
    """Создаёт клавиатуру для пустого списка."""
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_button("🔍 Начать поиск", color=VkKeyboardColor.POSITIVE)
    keyboard.add_line()
    keyboard.add_button("🏠 Главное меню", color=VkKeyboardColor.PRIMARY)
    return keyboard.get_keyboard()


def create_settings_keyboard():
    """Создаёт клавиатуру настроек."""
    keyboard = VkKeyboard(one_time=False)

    keyboard.add_button("📅 Изменить возраст", color=VkKeyboardColor.PRIMARY)
    keyboard.add_button("📍 Изменить расстояние", color=VkKeyboardColor.PRIMARY)

    keyboard.add_line()
    keyboard.add_button("🏠 Главное меню", color=VkKeyboardColor.SECONDARY)

    return keyboard.get_keyboard()


def create_admin_keyboard():
    """Создаёт клавиатуру админ-панели."""
    keyboard = VkKeyboard(one_time=False)

    keyboard.add_button("👥 Пользователи", color=VkKeyboardColor.PRIMARY)
    keyboard.add_button("📊 Статистика", color=VkKeyboardColor.PRIMARY)

    keyboard.add_line()
    keyboard.add_button(" Рассылка", color=VkKeyboardColor.POSITIVE)
    keyboard.add_button("🏠 Главное меню", color=VkKeyboardColor.SECONDARY)

    return keyboard.get_keyboard()
