import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Dict, List, Optional

# --- 1. Инфраструктура для Доменных Событий (упрощенная) ---


@dataclass(frozen=True)
class DomainEvent:
    """Базовый класс для всех доменных событий."""

    aggregate_id: uuid.UUID


# Простой обработчик/диспетчер событий для демонстрации
event_handlers: Dict[type, List[Callable]] = {}


def register_handler(event_type: type, handler: Callable):
    """Регистрирует обработчик для типа события."""
    if event_type not in event_handlers:
        event_handlers[event_type] = []
    event_handlers[event_type].append(handler)


def dispatch_event(event: DomainEvent):
    """Вызывает всех зарегистрированных обработчиков для данного события."""
    if type(event) in event_handlers:
        for handler in event_handlers[type(event)]:
            handler(event)


# --- 2. Value Objects и Enums ---


@dataclass(frozen=True)
class ShipmentId:
    value: uuid.UUID = field(default_factory=uuid.uuid4)


@dataclass(frozen=True)
class OrderId:
    """Ссылка на агрегат Заказа по ID."""

    value: uuid.UUID


@dataclass(frozen=True)
class Address:
    city: str
    street: str
    zip_code: str


@dataclass(frozen=True)
class Weight:
    value: float  # в килограммах

    def __post_init__(self):
        if self.value <= 0:
            raise ValueError("Вес должен быть положительным.")


@dataclass(frozen=True)
class Volume:
    value: float  # в кубических метрах

    def __post_init__(self):
        if self.value <= 0:
            raise ValueError("Объем должен быть положительным.")


class ShipmentStatus(Enum):
    PREPARING = "PREPARING"
    DISPATCHED = "DISPATCHED"
    IN_TRANSIT = "IN_TRANSIT"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"


# --- 3. Доменные События для Агрегата Shipment ---


@dataclass(frozen=True)
class ShipmentCreated(DomainEvent):
    destination: Address
    max_weight: Weight
    max_volume: Volume


@dataclass(frozen=True)
class ParcelAddedToShipment(DomainEvent):
    order_id: OrderId
    weight: Weight
    volume: Volume


@dataclass(frozen=True)
class ShipmentDispatched(DomainEvent):
    dispatch_timestamp: int


@dataclass(frozen=True)
class ShipmentDelivered(DomainEvent):
    delivery_timestamp: int


# --- 4. Сущности и Агрегат ---


@dataclass
class Parcel:  # Локальная сущность внутри агрегата
    order_id: OrderId
    weight: Weight
    volume: Volume

    def __hash__(self):
        return hash(self.order_id)

    def __eq__(self, other):
        if not isinstance(other, Parcel):
            return NotImplemented
        return self.order_id == other.order_id


class Shipment:
    """Агрегат "Отправление". Является корнем агрегата."""

    def __init__(self) -> None:
        # Конструктор намеренно оставлен простым.
        # Инициализация происходит через фабричный метод.
        self.id: Optional[ShipmentId] = None
        self.destination: Optional[Address] = None
        self.status: Optional[ShipmentStatus] = None
        self._parcels: List[Parcel] = []
        self._events: List[DomainEvent] = []
        self.max_weight: Optional[Weight] = None
        self.max_volume: Optional[Volume] = None
        self.version: int = 0

    @staticmethod
    def create(
        destination: Address, max_weight: Weight, max_volume: Volume
    ) -> "Shipment":
        """Фабричный метод для создания нового Отправления."""
        if not isinstance(destination, Address):
            raise TypeError("Некорректный тип адреса.")

        shipment = Shipment()
        shipment.id = ShipmentId()
        shipment.destination = destination
        shipment.status = ShipmentStatus.PREPARING
        shipment.max_weight = max_weight
        shipment.max_volume = max_volume
        shipment.version = 1

        event = ShipmentCreated(
            aggregate_id=shipment.id.value,
            destination=destination,
            max_weight=max_weight,
            max_volume=max_volume,
        )
        shipment._add_event(event)
        return shipment

    @property
    def parcels(self) -> List[Parcel]:
        return list(self._parcels)

    @property
    def current_weight(self) -> Weight:
        return (
            Weight(sum(p.weight.value for p in self._parcels))
            if self._parcels
            else Weight(0.001)
        )  # hack for positive value

    @property
    def current_volume(self) -> Volume:
        return (
            Volume(sum(p.volume.value for p in self._parcels))
            if self._parcels
            else Volume(0.001)
        )

    def _add_event(self, event: DomainEvent):
        self._events.append(event)

    def pull_domain_events(self) -> List[DomainEvent]:
        """Инфраструктурный метод для извлечения событий перед сохранением."""
        events = list(self._events)
        self._events.clear()
        return events

    def _increment_version(self):
        self.version += 1

    def add_parcel(self, order_id: OrderId, weight: Weight, volume: Volume):
        """Добавление посылки в отправление с проверкой инвариантов."""
        if self.status is not ShipmentStatus.PREPARING:
            actual_status_display = (
                self.status.value
                if self.status is not None
                else "None (не инициализирован)"
            )
            raise ValueError(
                "Нельзя добавлять посылки в отправление. "
                f"Текущий статус: {actual_status_display}, "
                f"ожидался: {ShipmentStatus.PREPARING}."
            )

        # Инвариант: не превышать максимальный вес
        if self.max_weight is None:
            raise RuntimeError(
                "Ошибка конфигурации Отправления: max_weight не установлен."
            )
        if self.current_weight.value + weight.value > self.max_weight.value:
            raise ValueError("Превышен максимальный вес отправления.")

        # Инвариант: не превышать максимальный объем
        if self.max_volume is None:
            raise RuntimeError(
                "Ошибка конфигурации Отправления: max_volume не установлен."
            )
        if self.current_volume.value + volume.value > self.max_volume.value:
            raise ValueError("Превышен максимальный объем отправления.")

        # Инвариант: одна посылка на один заказ
        if any(p.order_id == order_id for p in self._parcels):
            raise ValueError(
                f"Посылка для заказа {order_id.value} уже в этом отправлении."
            )

        parcel = Parcel(order_id=order_id, weight=weight, volume=volume)
        self._parcels.append(parcel)
        self._increment_version()

        if self.id is None:
            # Это состояние не должно быть достижимо, если объект создан через фабрику
            raise RuntimeError(
                "Shipment ID is not initialized when adding parcel event."
            )
        event = ParcelAddedToShipment(
            aggregate_id=self.id.value, order_id=order_id, weight=weight, volume=volume
        )
        self._add_event(event)

    def dispatch(self, timestamp: int):
        """Отправка груза."""
        if self.status != ShipmentStatus.PREPARING:
            raise ValueError("Отправить можно только подготовленный груз.")
        if not self._parcels:
            raise ValueError("Нельзя отправить пустой груз.")

        self.status = ShipmentStatus.DISPATCHED
        self._increment_version()
        if self.id is None:
            # Это состояние не должно быть достижимо
            raise RuntimeError("Shipment ID is not initialized when dispatching.")
        self._add_event(
            ShipmentDispatched(aggregate_id=self.id.value, dispatch_timestamp=timestamp)
        )

    def mark_as_delivered(self, timestamp: int):
        current_status_value = (
            self.status.value
            if self.status is not None
            else "None (не инициализирован)"
        )
        if self.status not in [ShipmentStatus.DISPATCHED, ShipmentStatus.IN_TRANSIT]:
            raise ValueError(
                f"Нельзя отметить доставленным груз в статусе {current_status_value}"
            )

        self.status = ShipmentStatus.DELIVERED
        self._increment_version()
        if self.id is None:
            # Это состояние не должно быть достижимо
            raise RuntimeError(
                "Shipment ID is not initialized when marking as delivered."
            )
        self._add_event(
            ShipmentDelivered(aggregate_id=self.id.value, delivery_timestamp=timestamp)
        )

    def __hash__(self):
        # Хеширование, работает, даже если self.id None.
        return hash((self.__class__, self.id))

    def __eq__(self, other):
        if not isinstance(other, Shipment):
            return NotImplemented
        # Если оба являются одним и тем же экземпляром, они равны
        if self is other:
            return True
        # Сравнение на основе класса и id
        return (self.__class__ is other.__class__) and (self.id == other.id)


# --- 5. Пример использования и обработчики событий ---


# Определим обработчики, которые будут "слушать" события
def handle_shipment_creation(event: ShipmentCreated):
    print(
        f"[Событие] Создано отправление {event.aggregate_id} "
        f"в {event.destination.city}. Макс. вес: {event.max_weight.value} кг."
    )


def handle_parcel_addition(event: ParcelAddedToShipment):
    print(
        f"[Событие] В отправление {event.aggregate_id} "
        f"добавлена посылка для заказа {event.order_id.value}."
    )


def handle_shipment_dispatch(event: ShipmentDispatched):
    print(
        f"[Событие] Отправление {event.aggregate_id} "
        f"отправлено в {event.dispatch_timestamp}."
    )


if __name__ == "__main__":
    # Регистрируем обработчики
    register_handler(ShipmentCreated, handle_shipment_creation)
    register_handler(ParcelAddedToShipment, handle_parcel_addition)
    register_handler(ShipmentDispatched, handle_shipment_dispatch)

    print("--- Демонстрация продвинутого Агрегата Shipment ---")

    # 1. Создание агрегата через фабрику
    dest_address = Address(city="Москва", street="Ленина", zip_code="101000")
    shipment = Shipment.create(dest_address, Weight(100.0), Volume(1.5))
    assert shipment.id is not None, "ID должен быть установлен фабрикой create()"
    assert (
        shipment.status is not None
    ), "Статус должен быть установлен фабрикой create()"
    print(
        f"\nСоздан агрегат Shipment ID: {shipment.id.value}, "
        f"Статус: {shipment.status.value}"
    )

    # Извлекаем и диспатчим события
    events = shipment.pull_domain_events()
    for e in events:
        dispatch_event(e)

    # 2. Добавление посылок
    try:
        print("\nДобавляем посылки...")
        shipment.add_parcel(OrderId(uuid.uuid4()), Weight(25.0), Volume(0.5))
        shipment.add_parcel(OrderId(uuid.uuid4()), Weight(50.0), Volume(0.8))

        events = shipment.pull_domain_events()
        for e in events:
            dispatch_event(e)

        print(
            f"Текущий вес: {shipment.current_weight.value} кг, "
            f"Объем: {shipment.current_volume.value} м3"
        )
        print(f"Версия агрегата: {shipment.version}")

    except ValueError as e:
        print("Ошибка добавления:")
        print(e)  # E501: line too long (82 > 79 characters)

    # 3. Попытка нарушить инвариант (превышение веса)
    try:
        print("\nПытаемся добавить слишком тяжелую посылку...")
        shipment.add_parcel(OrderId(uuid.uuid4()), Weight(30.0), Volume(0.1))
    except ValueError as e:
        print("Перехвачена ошибка:")
        print(e)  # E501: line too long (82 > 79 characters)

    # 4. Отправка груза
    try:
        print("\nОтправляем груз...")
        shipment.dispatch(timestamp=1678886400)
        assert (
            shipment.status is not None
        ), "Статус должен быть установлен после успешной отправки"
        print(f"Статус отправления: {shipment.status.value}")

        events = shipment.pull_domain_events()
        for evt in events:
            dispatch_event(evt)

    except ValueError as e:
        print(f"Ошибка: {e}")

    # 5. Попытка добавить посылку в отправленный груз
    try:
        print("\nПытаемся добавить посылку в уже отправленный груз...")
        shipment.add_parcel(OrderId(uuid.uuid4()), Weight(5.0), Volume(0.1))
    except ValueError as e:
        print(f"Перехвачена ошибка: {e}")
