"""
Интерфейсы (порты) для контекста проживания.

Определяет контракты, которые должны быть реализованы внешними адаптерами.
"""
from abc import ABC, abstractmethod
from datetime import date, datetime
from typing import List, Optional, Dict, Any, Protocol
from uuid import UUID

from ..shared_kernel import EntityId, DateRange
from .domain import (
    Room, Guest, CheckInRecord, CheckInStatus, RoomStatus,
    CheckIn, CheckOut, RoomMaintenanceScheduled
)


class IRoomRepository(Protocol):
    """Репозиторий для работы с номерами."""
    
    @abstractmethod
    def get_by_id(self, room_id: EntityId) -> Room:
        """Возвращает номер по идентификатору."""
        ...
    
    @abstractmethod
    def get_by_number(self, room_number: str) -> Room:
        """Возвращает номер по номеру комнаты."""
        ...
    
    @abstractmethod
    def find_available_rooms(
        self,
        check_in: date,
        check_out: date,
        room_type: Optional[str] = None,
        capacity: Optional[int] = None
    ) -> List[Room]:
        """Находит доступные номера по критериям."""
        ...
    
    @abstractmethod
    def update(self, room: Room) -> None:
        """Обновляет информацию о номере."""
        ...
    
    @abstractmethod
    def find_by_status(self, status: RoomStatus) -> List[Room]:
        """Находит все номера с указанным статусом."""
        ...


class IGuestRepository(Protocol):
    """Репозиторий для работы с гостями."""
    
    @abstractmethod
    def get_by_id(self, guest_id: EntityId) -> Guest:
        """Возвращает гостя по идентификатору."""
        ...
    
    @abstractmethod
    def find_by_name(self, first_name: str, last_name: str) -> List[Guest]:
        """Находит гостей по имени и фамилии."""
        ...
    
    @abstractmethod
    def find_by_document(self, document_number: str) -> Optional[Guest]:
        """Находит гостя по номеру документа."""
        ...
    
    @abstractmethod
    def add(self, guest: Guest) -> None:
        """Добавляет нового гостя."""
        ...
    
    @abstractmethod
    def update(self, guest: Guest) -> None:
        """Обновляет информацию о госте."""
        ...


class ICheckInRepository(Protocol):
    """Репозиторий для работы с заселениями."""
    
    @abstractmethod
    def get_by_id(self, check_in_id: EntityId) -> CheckInRecord:
        """Возвращает запись о заселении по идентификатору."""
        ...
    
    @abstractmethod
    def find_by_guest(self, guest_id: EntityId) -> List[CheckInRecord]:
        """Находит все заселения гостя."""
        ...
    
    @abstractmethod
    def find_by_room(self, room_id: EntityId) -> List[CheckInRecord]:
        """Находит все заселения в номере."""
        ...
    
    @abstractmethod
    def find_by_status(self, status: CheckInStatus) -> List[CheckInRecord]:
        """Находит все заселения с указанным статусом."""
        ...
    
    @abstractmethod
    def find_expected_arrivals(self, date: date) -> List[CheckInRecord]:
        """Находит ожидаемые заезды на указанную дату."""
        ...
    
    @abstractmethod
    def find_expected_departures(self, date: date) -> List[CheckInRecord]:
        """Находит ожидаемые выезды на указанную дату."""
        ...
    
    @abstractmethod
    def find_current_guests(self) -> List[CheckInRecord]:
        """Находит всех текущих гостей отеля."""
        ...
    
    @abstractmethod
    def add(self, check_in: CheckInRecord) -> None:
        """Добавляет новую запись о заселении."""
        ...
    
    @abstractmethod
    def update(self, check_in: CheckInRecord) -> None:
        """Обновляет запись о заселении."""
        ...


class IAccommodationUnitOfWork(Protocol):
    """Единица работы (Unit of Work) для контекста проживания."""
    
    @property
    def rooms(self) -> IRoomRepository:
        """Репозиторий номеров."""
        ...
    
    @property
    def guests(self) -> IGuestRepository:
        """Репозиторий гостей."""
        ...
    
    @property
    def check_ins(self) -> ICheckInRepository:
        """Репозиторий заселений."""
        ...
    
    def commit(self) -> None:
        """Фиксирует все изменения в рамках единицы работы."""
        ...
    
    def rollback(self) -> None:
        """Откатывает все изменения в рамках единицы работы."""
        ...


class IHousekeepingService(Protocol):
    """Сервис для управления уборкой номеров."""
    
    @abstractmethod
    def schedule_cleaning(self, room_id: EntityId, scheduled_time: datetime) -> None:
        """Планирует уборку номера."""
        ...
    
    @abstractmethod
    def mark_cleaning_completed(self, room_id: EntityId) -> None:
        """Отмечает уборку номера как выполненную."""
        ...
    
    @abstractmethod
    def get_rooms_due_for_cleaning(self) -> List[Dict[str, Any]]:
        """Возвращает список номеров, требующих уборки."""
        ...


class IMaintenanceService(Protocol):
    """Сервис для управления техническим обслуживанием."""
    
    @abstractmethod
    def schedule_maintenance(
        self,
        room_id: EntityId,
        start_time: datetime,
        end_time: datetime,
        reason: str
    ) -> None:
        """Планирует техническое обслуживание номера."""
        ...
    
    @abstractmethod
    def complete_maintenance(self, room_id: EntityId) -> None:
        """Завершает техническое обслуживание номера."""
        ...
    
    @abstractmethod
    def get_maintenance_schedule(self) -> List[Dict[str, Any]]:
        """Возвращает расписание технического обслуживания."""
        ...


class IEventPublisher(Protocol):
    """Абстракция для публикации доменных событий."""
    
    @abstractmethod
    def publish(self, event) -> None:
        """Публикует событие."""
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


class IEmailService(Protocol):
    """Сервис для отправки электронной почты."""
    
    @abstractmethod
    def send_email(
        self,
        to: str,
        subject: str,
        template_name: str,
        context: Dict[str, Any]
    ) -> bool:
        """
        Отправляет электронное письмо.
        
        Args:
            to: Адрес получателя
            subject: Тема письма
            template_name: Имя шаблона письма
            context: Контекст для шаблона
            
        Returns:
            True, если письмо успешно отправлено, иначе False
        """
        ...
