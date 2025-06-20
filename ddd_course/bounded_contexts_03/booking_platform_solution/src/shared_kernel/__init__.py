"""
Общее ядро (Shared Kernel) для системы управления отелем.

Содержит общие типы данных и утилиты, используемые в различных ограниченных контекстах.
"""

from .domain import (
    Address,
    BookingStatus,
    BusinessRuleValidationException,
    ConcurrencyException,
    DateRange,
    DomainEvent,
    # Исключения
    DomainException,
    # Базовые типы
    EntityId,
    # Основные классы
    Money,
    PaymentStatus,
    RoomStatus,
    # Перечисления
    RoomType,
    generate_id,
    # Утилиты
    now,
    today,
)

__all__ = [
    # Базовые типы
    "EntityId",
    "generate_id",
    # Основные классы
    "Money",
    "DateRange",
    "Address",
    "DomainEvent",
    # Перечисления
    "RoomType",
    "BookingStatus",
    "PaymentStatus",
    "RoomStatus",
    # Исключения
    "DomainException",
    "ConcurrencyException",
    "BusinessRuleValidationException",
    # Утилиты
    "now",
    "today",
]
