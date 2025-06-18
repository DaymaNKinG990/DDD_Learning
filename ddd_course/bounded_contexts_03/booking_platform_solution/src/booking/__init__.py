"""
Модуль контекста бронирования (Booking Context).

Отвечает за управление бронированием номеров в отеле, включая:
- Создание, отмену и изменение бронирований
- Проверку доступности номеров
- Управление состоянием бронирований
"""

from . import domain, application, infrastructure, interfaces

__all__ = [
    'domain',
    'application',
    'infrastructure',
    'interfaces',
]
