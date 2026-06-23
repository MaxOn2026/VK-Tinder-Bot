"""Модуль настройки логирования для VK-Tinder-Bot."""

import logging
import sys
from pathlib import Path

# Путь к директории логов
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

# Форматирование логов
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logger(name: str = "vkinder", level: int = logging.DEBUG) -> logging.Logger:
    """Настраивает и возвращает логгер с указанным именем.

    Args:
        name: Имя логгера (обычно __name__ модуля).
        level: Уровень логирования.

    Returns:
        Настроенный логгер.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Избегаем добавления handler'ов при повторных вызовах
    if logger.handlers:
        return logger

    # Консольный handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT))
    logger.addHandler(console_handler)

    # File handler — отладочный лог
    debug_file = LOG_DIR / "debug.log"
    file_handler = logging.FileHandler(debug_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s.%(funcName)s:%(lineno)d: %(message)s",
        datefmt=DATE_FORMAT,
    ))
    logger.addHandler(file_handler)

    # Error handler — отдельный файл ошибок
    error_file = LOG_DIR / "error.log"
    error_handler = logging.FileHandler(error_file, encoding="utf-8")
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s.%(funcName)s:%(lineno)d: %(message)s",
        datefmt=DATE_FORMAT,
    ))
    logger.addHandler(error_handler)

    return logger
