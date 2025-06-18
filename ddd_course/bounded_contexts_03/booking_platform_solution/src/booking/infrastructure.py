"""
Инфраструктурный слой контекста бронирования.

Содержит реализации репозиториев и других интерфейсов,
зависимые от конкретных технологий (БД, внешние сервисы и т.д.).
"""
import json
from datetime import date
from pathlib import Path
from typing import Dict, List, Optional, Set, Type, TypeVar, Any, cast
from uuid import UUID

from pydantic import BaseModel, parse_raw_as

from ..shared_kernel import EntityId, DateRange, DomainEvent, BookingStatus
from . import interfaces as ports
from .domain import Booking, Room, Guest

T = TypeVar('T', bound=BaseModel)


class JsonFileRepository:
    """Базовый класс для репозиториев, работающих с JSON-файлами."""
    
    def __init__(self, file_path: str, model_class: Type[T]):
        """
        Инициализирует репозиторий.
        
        Args:
            file_path: Путь к JSON-файлу с данными
            model_class: Класс модели данных
        """
        self._file_path = Path(file_path)
        self._model_class = model_class
        self._data: Dict[EntityId, T] = {}
        self._load_data()
    
    def _load_data(self) -> None:
        """Загружает данные из JSON-файла."""
        if not self._file_path.exists():
            self._data = {}
            return
        
        with open(self._file_path, 'r', encoding='utf-8') as f:
            raw_data = f.read()
        
        if not raw_data.strip():
            self._data = {}
            return
            
        items = json.loads(raw_data)
        self._data = {
            UUID(item['id']): self._model_class.parse_obj(item)
            for item in items
        }
    
    def _save_data(self) -> None:
        """Сохраняет данные в JSON-файл."""
        # Создаем директорию, если она не существует
        self._file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Преобразуем данные в JSON-совместимый формат
        data = [item.dict() for item in self._data.values()]
        
        # Сохраняем в файл с отступами для читаемости
        with open(self._file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)


class InMemoryBookingRepository(ports.IBookingRepository):
    """Реализация репозитория бронирований в памяти."""
    
    def __init__(self):
        self._bookings: Dict[EntityId, Booking] = {}
        self._next_id = 1
    
    def get_by_id(self, booking_id: EntityId) -> Booking:
        if booking_id not in self._bookings:
            raise KeyError(f"Booking with id {booking_id} not found")
        return self._bookings[booking_id]
    
    def add(self, booking: Booking) -> None:
        if booking.id in self._bookings:
            raise ValueError(f"Booking with id {booking.id} already exists")
        self._bookings[booking.id] = booking
    
    def update(self, booking: Booking) -> None:
        if booking.id not in self._bookings:
            raise KeyError(f"Booking with id {booking.id} not found")
        self._bookings[booking.id] = booking
    
    def find_by_guest(self, guest_id: EntityId) -> List[Booking]:
        return [
            booking for booking in self._bookings.values()
            if booking.guest_id == guest_id
        ]
    
    def find_by_status(self, status: BookingStatus) -> List[Booking]:
        return [
            booking for booking in self._bookings.values()
            if booking.status == status
        ]
    
    def find_overlapping_bookings(
        self,
        room_id: EntityId,
        check_in: date,
        check_out: date,
        exclude_booking_id: Optional[EntityId] = None
    ) -> List[Booking]:
        result = []
        
        for booking in self._bookings.values():
            # Пропускаем исключенное бронирование
            if exclude_booking_id is not None and booking.id == exclude_booking_id:
                continue
                
            # Проверяем пересечение периодов
            if (booking.room_id == room_id and
                booking.status in (BookingStatus.PENDING, BookingStatus.CONFIRMED) and
                booking.period.check_in < check_out and
                booking.period.check_out > check_in):
                result.append(booking)
        
        return result


class InMemoryRoomRepository(ports.IRoomRepository):
    """Реализация репозитория номеров в памяти."""
    
    def __init__(self):
        self._rooms: Dict[EntityId, Room] = {}
        self._initialize_sample_data()
    
    def _initialize_sample_data(self) -> None:
        """Инициализирует тестовые данные."""
        from ..shared_kernel import RoomType, Money
        
        sample_rooms = [
            Room(
                id=UUID('11111111-1111-1111-1111-111111111111'),
                number="101",
                type=RoomType.STANDARD,
                capacity=2,
                amenities=["TV", "Wi-Fi", "Mini-bar"],
                base_price_per_night=Money(amount=3500.0)
            ),
            Room(
                id=UUID('22222222-2222-2222-2222-222222222222'),
                number="201",
                type=RoomType.DELUXE,
                capacity=2,
                amenities=["TV", "Wi-Fi", "Mini-bar", "Sea View"],
                base_price_per_night=Money(amount=5000.0)
            ),
            Room(
                id=UUID('33333333-3333-3333-3333-333333333333'),
                number="301",
                type=RoomType.SUITE,
                capacity=4,
                amenities=["TV", "Wi-Fi", "Mini-bar", "Sea View", "Jacuzzi"],
                base_price_per_night=Money(amount=10000.0)
            ),
            Room(
                id=UUID('44444444-4444-4444-4444-444444444444'),
                number="401",
                type=RoomType.FAMILY,
                capacity=6,
                amenities=["TV", "Wi-Fi", "Kitchen", "Balcony"],
                base_price_per_night=Money(amount=15000.0)
            ),
        ]
        
        for room in sample_rooms:
            self._rooms[room.id] = room
    
    def get_by_id(self, room_id: EntityId) -> Room:
        if room_id not in self._rooms:
            raise KeyError(f"Room with id {room_id} not found")
        return self._rooms[room_id]
    
    def find_available_rooms(
        self,
        room_type: Optional[str] = None,
        capacity: Optional[int] = None,
        check_in: Optional[date] = None,
        check_out: Optional[date] = None
    ) -> List[Room]:
        # В реальном приложении здесь была бы проверка доступности
        # по датам через репозиторий бронирований
        return list(self._rooms.values())


class InMemoryGuestRepository(ports.IGuestRepository):
    """Реализация репозитория гостей в памяти."""
    
    def __init__(self):
        self._guests: Dict[EntityId, Guest] = {}
        self._email_index: Dict[str, Guest] = {}
        self._initialize_sample_data()
    
    def _initialize_sample_data(self) -> None:
        """Инициализирует тестовые данные."""
        sample_guests = [
            Guest(
                id=UUID('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'),
                first_name="Иван",
                last_name="Иванов",
                email="ivan.ivanov@example.com",
                phone="+79101234567",
                document_number="1234567890"
            ),
            Guest(
                id=UUID('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb'),
                first_name="Петр",
                last_name="Петров",
                email="petr.petrov@example.com",
                phone="+79111234567",
                document_number="0987654321"
            ),
        ]
        
        for guest in sample_guests:
            self.add(guest)
    
    def get_by_id(self, guest_id: EntityId) -> Guest:
        if guest_id not in self._guests:
            raise KeyError(f"Guest with id {guest_id} not found")
        return self._guests[guest_id]
    
    def find_by_email(self, email: str) -> Optional[Guest]:
        return self._email_index.get(email.lower())
    
    def add(self, guest: Guest) -> None:
        if guest.id in self._guests:
            raise ValueError(f"Guest with id {guest.id} already exists")
        if guest.email.lower() in self._email_index:
            raise ValueError(f"Guest with email {guest.email} already exists")
        
        self._guests[guest.id] = guest
        self._email_index[guest.email.lower()] = guest


class ConsoleLogger(ports.ILogger):
    """Простая реализация логгера, выводящая сообщения в консоль."""
    
    def info(self, message: str, **kwargs) -> None:
        print(f"[INFO] {message}", flush=True)
        if kwargs:
            print("  Context:", json.dumps(kwargs, default=str, indent=2), flush=True)
    
    def error(self, message: str, **kwargs) -> None:
        print(f"[ERROR] {message}", file=sys.stderr, flush=True)
        if kwargs:
            print("  Context:", json.dumps(kwargs, default=str, indent=2), file=sys.stderr, flush=True)
    
    def warning(self, message: str, **kwargs) -> None:
        print(f"[WARNING] {message}", file=sys.stderr, flush=True)
        if kwargs:
            print("  Context:", json.dumps(kwargs, default=str, indent=2), file=sys.stderr, flush=True)


class InMemoryEventBus(ports.IEventBus):
    """Реализация шины событий в памяти."""
    
    def __init__(self, logger: Optional[ports.ILogger] = None):
        self._subscribers: Dict[Type[DomainEvent], list] = {}
        self._logger = logger or ConsoleLogger()
    
    def publish(self, event: DomainEvent) -> None:
        """Публикует событие."""
        event_type = type(event)
        if event_type not in self._subscribers:
            self._logger.debug(f"No subscribers for event type {event_type.__name__}")
            return
        
        self._logger.info(f"Publishing event: {event_type.__name__}", event=event.dict())
        
        for handler in self._subscribers[event_type]:
            try:
                handler(event)
            except Exception as e:
                self._logger.error(
                    f"Error in event handler for {event_type.__name__}",
                    error=str(e),
                    event=event.dict()
                )
    
    def subscribe(self, event_type: Type[DomainEvent], handler) -> None:
        """Подписывает обработчик на события указанного типа."""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)
        self._logger.debug(f"Subscribed handler to {event_type.__name__} events")


class BookingUnitOfWork(ports.IBookingUnitOfWork):
    """Единица работы для контекста бронирования."""
    
    def __init__(
        self,
        bookings_repo: Optional[ports.IBookingRepository] = None,
        rooms_repo: Optional[ports.IRoomRepository] = None,
        guests_repo: Optional[ports.IGuestRepository] = None,
        logger: Optional[ports.ILogger] = None
    ):
        self._bookings = bookings_repo or InMemoryBookingRepository()
        self._rooms = rooms_repo or InMemoryRoomRepository()
        self._guests = guests_repo or InMemoryGuestRepository()
        self._logger = logger or ConsoleLogger()
        self._committed = False
    
    @property
    def bookings(self) -> ports.IBookingRepository:
        return self._bookings
    
    @property
    def rooms(self) -> ports.IRoomRepository:
        return self._rooms
    
    @property
    def guests(self) -> ports.IGuestRepository:
        return self._guests
    
    def commit(self) -> None:
        """Фиксирует все изменения."""
        # В реальном приложении здесь была бы фиксация транзакции
        self._committed = True
        self._logger.info("BookingUnitOfWork committed")
    
    def rollback(self) -> None:
        """Откатывает все изменения."""
        # В реальном приложении здесь был бы откат транзакции
        self._committed = False
        self._logger.warning("BookingUnitOfWork rolled back")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.commit()
        else:
            self.rollback()
        return False  # Пробрасываем исключение дальше, если оно было
