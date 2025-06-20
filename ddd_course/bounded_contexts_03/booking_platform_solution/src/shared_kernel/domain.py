"""
Основные доменные типы и утилиты общего ядра.
"""

from datetime import date, datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, validator

# Общие типы идентификаторов
EntityId = UUID


def generate_id() -> UUID:
    """Генерирует новый UUID."""
    return uuid4()


class Money(BaseModel):
    """Денежная сумма с валютой."""

    amount: float = Field(..., ge=0, description="Сумма денег")
    currency: str = Field(
        default="RUB", max_length=3, description="Код валюты (ISO 4217)"
    )

    def __add__(self, other: "Money") -> "Money":
        if not isinstance(other, Money):
            raise TypeError("Можно складывать только объекты Money")
        if self.currency != other.currency:
            raise ValueError("Нельзя складывать разные валюты")
        return Money(amount=self.amount + other.amount, currency=self.currency)

    def __sub__(self, other: "Money") -> "Money":
        if not isinstance(other, Money):
            raise TypeError("Можно вычитать только объекты Money")
        if self.currency != other.currency:
            raise ValueError("Нельзя вычитать разные валюты")
        if self.amount < other.amount:
            raise ValueError("Результат не может быть отрицательным")
        return Money(amount=self.amount - other.amount, currency=self.currency)

    def __mul__(self, multiplier: float) -> "Money":
        if not isinstance(multiplier, (int, float)):
            raise TypeError("Множитель должен быть числом")
        if multiplier < 0:
            raise ValueError("Множитель не может быть отрицательным")
        return Money(amount=self.amount * multiplier, currency=self.currency)


class DateRange(BaseModel):
    """Диапазон дат."""

    check_in: date
    check_out: date

    @validator("check_out")
    def check_out_after_check_in(cls, v, values):
        if "check_in" in values and v <= values["check_in"]:
            raise ValueError("Дата выезда должна быть позже даты заезда")
        return v

    @property
    def nights(self) -> int:
        """Количество ночей в бронировании."""
        return (self.check_out - self.check_in).days


class Address(BaseModel):
    """Почтовый адрес."""

    country: str
    city: str
    street: str
    building: str
    apartment: Optional[str] = None
    postal_code: str


class DomainEvent(BaseModel):
    """Базовый класс для всех доменных событий."""

    event_id: UUID = Field(default_factory=uuid4)
    occurred_on: datetime = Field(default_factory=datetime.utcnow)
    event_type: str

    class Config:
        arbitrary_types_allowed = True


# Общие перечисления
class RoomType(str, Enum):
    """Типы номеров в отеле."""

    STANDARD = "standard"
    DELUXE = "deluxe"
    SUITE = "suite"
    FAMILY = "family"


class BookingStatus(str, Enum):
    """Статусы бронирования."""

    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class PaymentStatus(str, Enum):
    """Статусы платежей."""

    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"


class RoomStatus(str, Enum):
    """Статусы номеров."""

    AVAILABLE = "available"
    OCCUPIED = "occupied"
    MAINTENANCE = "maintenance"
    CLEANING = "cleaning"


# Общие исключения
class DomainException(Exception):
    """Базовое исключение для доменных ошибок."""

    pass


class ConcurrencyException(DomainException):
    """Исключение при конфликте версий."""

    pass


class BusinessRuleValidationException(DomainException):
    """Исключение при нарушении бизнес-правил."""

    pass


# Общие утилиты
def now() -> datetime:
    """Возвращает текущую дату и время."""
    return datetime.utcnow()


def today() -> date:
    """Возвращает текущую дату."""
    return date.today()
