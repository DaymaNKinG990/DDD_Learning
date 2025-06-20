"""
Интерфейсы (порты) для контекста бронирования.

Определяет контракты, которые должны быть реализованы внешними адаптерами.
"""

from abc import abstractmethod
from datetime import date
from typing import Callable, List, Optional, Protocol, Type, TypeVar

from ..shared_kernel import DateRange, DomainEvent, EntityId  # Добавлен DomainEvent
from .domain import Booking, BookingStatus, Guest, Room

T_Event = TypeVar("T_Event", bound=DomainEvent)  # Для ковариантности событий


class IBookingRepository(Protocol):
    """Репозиторий для работы с бронированиями."""

    @abstractmethod
    def get_by_id(self, booking_id: EntityId) -> Booking:
        """Возвращает бронирование по идентификатору."""
        ...

    @abstractmethod
    def add(self, booking: Booking) -> None:
        """Добавляет новое бронирование."""
        ...

    @abstractmethod
    def update(self, booking: Booking) -> None:
        """Обновляет существующее бронирование."""
        ...

    @abstractmethod
    def find_by_guest(self, guest_id: EntityId) -> List[Booking]:
        """Находит все бронирования гостя."""
        ...

    @abstractmethod
    def find_by_status(self, status: BookingStatus) -> List[Booking]:
        """Находит все бронирования с указанным статусом."""
        ...

    @abstractmethod
    def find_overlapping_bookings(
        self,
        room_id: EntityId,
        check_in: DateRange,
        check_out: DateRange,
        exclude_booking_id: Optional[EntityId] = None,
    ) -> List[Booking]:
        """
        Находит все бронирования, которые пересекаются с указанным периодом.

        Args:
            room_id: Идентификатор номера
            check_in: Дата заезда
            check_out: Дата выезда
            exclude_booking_id: Исключить бронирование с указанным ID

        Returns:
            Список пересекающихся бронирований
        """
        ...


class IRoomRepository(Protocol):
    """Репозиторий для работы с номерами."""

    @abstractmethod
    def get_by_id(self, room_id: EntityId) -> Room:
        """Возвращает номер по идентификатору."""
        ...

    @abstractmethod
    def find_available_rooms(
        self,
        room_type: Optional[str] = None,
        capacity: Optional[int] = None,
        check_in: Optional[date] = None,
        check_out: Optional[date] = None,
    ) -> List[Room]:
        """Находит доступные номера по критериям."""
        ...


class IGuestRepository(Protocol):
    """Репозиторий для работы с гостями."""

    @abstractmethod
    def get_by_id(self, guest_id: EntityId) -> Guest:
        """Возвращает гостя по идентификатору."""
        ...

    @abstractmethod
    def find_by_email(self, email: str) -> Optional[Guest]:
        """Находит гостя по email."""
        ...

    @abstractmethod
    def add(self, guest: Guest) -> None:
        """Добавляет нового гостя."""
        ...


class IBookingUnitOfWork(Protocol):
    """Единица работы (Unit of Work) для контекста бронирования."""

    @property
    def bookings(self) -> IBookingRepository:
        """Репозиторий бронирований."""
        ...

    @property
    def rooms(self) -> IRoomRepository:
        """Репозиторий номеров."""
        ...

    @property
    def guests(self) -> IGuestRepository:
        """Репозиторий гостей."""
        ...

    def commit(self) -> None:
        """Фиксирует все изменения в рамках единицы работы."""
        ...

    def rollback(self) -> None:
        """Откатывает все изменения в рамках единицы работы."""
        ...


class IBookingNotifier(Protocol):
    """Сервис уведомлений о бронированиях."""

    @abstractmethod
    def send_booking_confirmation(self, booking: Booking) -> None:
        """Отправляет подтверждение бронирования."""
        ...

    @abstractmethod
    def send_booking_cancellation(
        self, booking: Booking, reason: Optional[str] = None
    ) -> None:
        """Отправляет уведомление об отмене бронирования."""
        ...

    @abstractmethod
    def send_booking_reminder(self, booking: Booking) -> None:
        """Отправляет напоминание о предстоящем заезде."""
        ...


class IEventBus(Protocol):
    """Шина событий для публикации доменных событий."""

    @abstractmethod
    def publish(self, event: DomainEvent) -> None:  # Типизирован event
        """Публикует событие."""
        ...

    @abstractmethod
    def subscribe(
        self, event_type: Type[T_Event], handler: Callable[[T_Event], None]
    ) -> None:  # Улучшена типизация
        """Подписывает обработчик на события указанного типа."""
        ...


class ILogger(Protocol):
    """Абстракция для логирования."""

    @abstractmethod
    def info(self, message: str, **kwargs) -> None:
        """Записывает информационное сообщение."""
        ...

    @abstractmethod
    def error(self, message: str, **kwargs) -> None:
        """Записывает сообщение об ошибке."""
        ...

    @abstractmethod
    def warning(self, message: str, **kwargs) -> None:
        """Записывает предупреждение."""
        ...

    @abstractmethod
    def debug(self, message: str, **kwargs) -> None:
        """Записывает отладочное сообщение."""
        ...
