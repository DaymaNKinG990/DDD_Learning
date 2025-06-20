"""
Модуль контекста проживания (Accommodation Context).

Отвечает за управление заселением и выселением гостей, а также
за отслеживание состояния номеров в отеле.
"""

from . import application, domain, infrastructure, interfaces

__all__ = [
    "domain",
    "application",
    "infrastructure",
    "interfaces",
]
