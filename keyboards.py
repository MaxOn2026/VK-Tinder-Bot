"""Модуль для создания клавиатур."""
from vk_api.keyboard import VkKeyboard, VkKeyboardColor


def create_main_keyboard():
    """Главная клавиатура с кнопками."""
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_button('Начать поиск', color=VkKeyboardColor.POSITIVE)
    keyboard.add_button('Дальше', color=VkKeyboardColor.PRIMARY)
    keyboard.add_button('В избранное', color=VkKeyboardColor.SECONDARY)
    return keyboard.get_keyboard()