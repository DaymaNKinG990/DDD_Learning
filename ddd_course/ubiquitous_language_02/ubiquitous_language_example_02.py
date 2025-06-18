"""
Пример применения Ubiquitous Language в Python-коде.

Этот модуль демонстрирует, как единый язык предметной области
может быть отражён в коде на примере системы бронирования отелей.
"""
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import List, Optional
from uuid import UUID, uuid4


# ============================================
# Value Objects (Объекты-значения)
# ============================================

@dataclass(frozen=True)
class Money:
    """Денежная сумма с валютой.
    
    Атрибуты:
        amount: Сумма
        currency: Валюта (код из трёх букв, например, 'RUB', 'USD')
    """
    amount: float
    currency: str = "RUB"

    def __post_init__(self):
        if self.amount < 0:
            raise ValueError("Сумма не может быть отрицательной")
        if len(self.currency) != 3 or not self.currency.isalpha():
            raise ValueError("Неверный формат валюты. Используйте трёхбуквенный код (например, 'RUB')")


@dataclass(frozen=True)
class DateRange:
    """Диапазон дат (например, период проживания).
    
    Атрибуты:
        check_in: Дата заезда
        check_out: Дата выезда
    """
    check_in: date
    check_out: date

    def __post_init__(self):
        if self.check_in >= self.check_out:
            raise ValueError("Дата заезда должна быть раньше даты выезда")
        if (self.check_out - self.check_in).days > 30:
            raise ValueError("Максимальный срок проживания - 30 дней")
    
    @property
    def nights(self) -> int:
        """Количество ночей в брони."""
        return (self.check_out - self.check_in).days


# ============================================
# Entities (Сущности)
# ============================================

@dataclass
class RoomType:
    """Тип номера в отеле.
    
    Атрибуты:
        id: Уникальный идентификатор типа номера
        name: Название типа номера (например, 'Стандарт', 'Люкс')
        description: Описание номера
        max_occupancy: Максимальное количество гостей
    """
    id: UUID
    name: str
    description: str
    max_occupancy: int


@dataclass
class Room:
    """Номер в отеле.
    
    Атрибуты:
        number: Номер комнаты (уникальный идентификатор)
        room_type: Тип номера
        floor: Этаж
        is_available: Доступен ли номер для бронирования
    """
    number: str
    room_type: RoomType
    floor: int
    is_available: bool = True


@dataclass
class Guest:
    """Гость отеля.
    
    Атрибуты:
        id: Уникальный идентификатор гостя
        first_name: Имя
        last_name: Фамилия
        email: Адрес электронной почты
        phone: Номер телефона
    """
    id: UUID
    first_name: str
    last_name: str
    email: str
    phone: str
    
    @property
    def full_name(self) -> str:
        """Полное имя гостя."""
        return f"{self.first_name} {self.last_name}"


@dataclass
class Booking:
    """Бронь номера в отеле.
    
    Атрибуты:
        id: Уникальный идентификатор брони
        guest: Гость, сделавший бронь
        room: Забронированный номер
        stay_period: Период проживания
        status: Статус брони (подтверждена, отменена, выполнена)
        created_at: Дата и время создания брони
        total_price: Общая стоимость проживания
    """
    id: UUID
    guest: Guest
    room: Room
    stay_period: DateRange
    status: str = "подтверждена"
    created_at: date = field(default_factory=date.today)
    total_price: Optional[Money] = None
    
    def cancel(self) -> None:
        """Отменить бронирование."""
        if self.status == "отменена":
            raise ValueError("Бронь уже отменена")
        if self.status == "выполнена":
            raise ValueError("Нельзя отменить завершённое бронирование")
        self.status = "отменена"
    
    def check_in(self) -> None:
        """Оформить заезд гостя."""
        if self.status != "подтверждена":
            raise ValueError("Невозможно заехать по отменённой или выполненной брони")
        if self.stay_period.check_in != date.today():
            raise ValueError("Заезд возможен только в день заезда")
        if not self.room.is_available:
            raise ValueError("Номер уже занят")
        
        self.room.is_available = False
        print(f"Гость {self.guest.full_name} заселяется в номер {self.room.number}")
    
    def check_out(self) -> None:
        """Оформить выезд гостя."""
        if self.room.is_available:
            raise ValueError("Номер уже свободен")
        
        self.room.is_available = True
        self.status = "выполнена"
        print(f"Гость {self.guest.full_name} выселяется из номера {self.room.number}")


# ============================================
# Domain Service (Доменный сервис)
# ============================================

class BookingService:
    """Сервис для работы с бронированиями."""
    
    def __init__(self, room_repository):
        self.room_repository = room_repository
    
    def find_available_rooms(
        self,
        room_type: RoomType,
        stay_period: DateRange,
        guests: int
    ) -> List[Room]:
        """Найти доступные номера указанного типа на заданный период.
        
        Аргументы:
            room_type: Тип номера
            stay_period: Период проживания
            guests: Количество гостей
            
        Возвращает:
            Список доступных номеров
        """
        if guests > room_type.max_occupancy:
            raise ValueError(f"Превышено максимальное количество гостей для данного типа номера: {room_type.max_occupancy}")
        
        # В реальном приложении здесь был бы запрос к репозиторию
        all_rooms = self.room_repository.find_by_room_type(room_type.id)
        available_rooms = [
            room for room in all_rooms 
            if self._is_room_available(room, stay_period)
        ]
        
        return available_rooms
    
    def _is_room_available(self, room: Room, stay_period: DateRange) -> bool:
        """Проверить, доступен ли номер на указанный период."""
        # В реальном приложении здесь была бы проверка в базе данных
        # о существующих бронях на этот номер и период
        return room.is_available
    
    def calculate_booking_price(
        self,
        room: Room,
        stay_period: DateRange,
        is_weekend_surcharge: bool = False
    ) -> Money:
        """Рассчитать стоимость бронирования.
        
        Аргументы:
            room: Номер для бронирования
            stay_period: Период проживания
            is_weekend_surcharge: Применять ли надбавку за выходные
            
        Возвращает:
            Общая стоимость проживания
        """
        # Базовая стоимость за ночь (в реальном приложении бралась бы из базы)
        base_price_per_night = 5000.0  # руб.
        
        # Надбавка за выходные (30%)
        weekend_multiplier = 1.3 if is_weekend_surcharge else 1.0
        
        # Рассчитываем общую стоимость
        total_amount = base_price_per_night * stay_period.nights * weekend_multiplier
        
        return Money(amount=total_amount, currency="RUB")


# ============================================
# Пример использования
# ============================================

def demonstrate_ubiquitous_language():
    """Демонстрация использования единого языка в коде."""
    print("=== Демонстрация Ubiquitous Language в системе бронирования отелей ===\n")
    
    # Создаём типы номеров
    standard_room_type = RoomType(
        id=uuid4(),
        name="Стандарт",
        description="Стандартный номер с одной двуспальной кроватью",
        max_occupancy=2
    )
    
    # Создаём номера
    room_101 = Room(number="101", room_type=standard_room_type, floor=1)
    room_102 = Room(number="102", room_type=standard_room_type, floor=1)
    
    # Создаём гостя
    guest = Guest(
        id=uuid4(),
        first_name="Иван",
        last_name="Иванов",
        email="ivan@example.com",
        phone="+79161234567"
    )
    
    # Создаём период проживания
    check_in = date.today() + timedelta(days=7)
    check_out = check_in + timedelta(days=3)
    stay_period = DateRange(check_in=check_in, check_out=check_out)
    
    # Инициализируем сервис бронирования
    # В реальном приложении репозиторий инжектировался бы через DI
    class MockRoomRepository:
        def find_by_room_type(self, room_type_id):
            return [room_101, room_102]
    
    booking_service = BookingService(room_repository=MockRoomRepository())
    
    # Ищем доступные номера
    available_rooms = booking_service.find_available_rooms(
        room_type=standard_room_type,
        stay_period=stay_period,
        guests=2
    )
    
    print(f"Доступно номеров: {len(available_rooms)}")
    
    if available_rooms:
        # Выбираем первый доступный номер
        selected_room = available_rooms[0]
        
        # Рассчитываем стоимость
        total_price = booking_service.calculate_booking_price(
            room=selected_room,
            stay_period=stay_period,
            is_weekend_surcharge=True
        )
        
        # Создаём бронь
        booking = Booking(
            id=uuid4(),
            guest=guest,
            room=selected_room,
            stay_period=stay_period,
            total_price=total_price
        )
        
        print(f"\nСоздана бронь #{booking.id}:")
        print(f"Гость: {booking.guest.full_name}")
        print(f"Номер: {booking.room.number} ({booking.room.room_type.name})")
        print(f"Период: {booking.stay_period.check_in} - {booking.stay_period.check_out}")
        print(f"Стоимость: {booking.total_price.amount} {booking.total_price.currency}")
        
        # Симулируем заезд (если сегодня день заезда)
        if date.today() == check_in:
            try:
                booking.check_in()
                # ... через несколько дней
                booking.check_out()
            except ValueError as e:
                print(f"Ошибка: {e}")


if __name__ == "__main__":
    demonstrate_ubiquitous_language()
