# Решение упражнения по модулю "Репозитории (Repositories)"

## Задание: Реализация Репозитория для Агрегата `Order`

Ниже представлен пример реализации интерфейса `OrderRepository` и его "in-memory" версии `InMemoryOrderRepository`, а также необходимые доменные классы и примеры использования.

### Код решения

```python
from __future__ import annotations

import abc
import copy
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import List, NewType, Optional, Dict, Tuple, TypeVar

# --- Вспомогательные типы и классы из предыдущих модулей ---

OrderId = NewType("OrderId", uuid.UUID)
OrderItemId = NewType("OrderItemId", uuid.UUID)
CustomerId = NewType("CustomerId", uuid.UUID)
ProductId = NewType("ProductId", uuid.UUID)

_TMoney = TypeVar("_TMoney", bound="Money")


@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: str = "USD"

    def __post_init__(self):
        if self.amount < Decimal(0):
            raise ValueError("Amount cannot be negative.")
        if not self.currency or len(self.currency) != 3:
            raise ValueError("Currency must be a 3-letter code.")

    def __add__(self: _TMoney, other: _TMoney) -> _TMoney:
        if not isinstance(other, Money) or self.currency != other.currency:
            raise ValueError("Cannot add Money with different currencies.")
        return self.__class__(self.amount + other.amount, self.currency)

    def __sub__(self: _TMoney, other: _TMoney) -> _TMoney:
        if not isinstance(other, Money) or self.currency != other.currency:
            raise ValueError("Cannot subtract Money with different currencies.")
        return self.__class__(self.amount - other.amount, self.currency)

    def __mul__(self: _TMoney, multiplier: int | Decimal) -> _TMoney:
        if not isinstance(multiplier, (int, Decimal)) or multiplier < 0:
            raise ValueError("Multiplier must be a non-negative number.")
        return self.__class__(self.amount * Decimal(multiplier), self.currency)

    @classmethod
    def zero(cls: type[_TMoney], currency: str = "USD") -> _TMoney:
        return cls(Decimal(0), currency)


@dataclass(frozen=True)
class ShippingAddress:
    street: str
    city: str
    postal_code: str
    country: str

    def __post_init__(self):
        if not all([self.street, self.city, self.postal_code, self.country]):
            raise ValueError("All address fields must be provided.")


class OrderStatus(Enum):
    PENDING = "pending"
    PAID = "paid"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


@dataclass
class OrderItem:
    order_item_id: OrderItemId
    product_id: ProductId
    quantity: int
    price_per_unit: Money

    def __post_init__(self):
        if self.quantity <= 0:
            raise ValueError("Quantity must be positive.")

    def calculate_item_total(self) -> Money:
        return self.price_per_unit * self.quantity

    def _update_quantity(self, new_quantity: int) -> None:
        if new_quantity <= 0:
            raise ValueError("New quantity must be positive.")
        self.quantity = new_quantity

# --- Доменные События (из предыдущего модуля) ---
@dataclass(frozen=True)
class DomainEvent:
    event_id: uuid.UUID = field(default_factory=uuid.uuid4)
    occurred_on: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

@dataclass(frozen=True)
class OrderCreatedEvent(DomainEvent):
    order_id: OrderId
    customer_id: CustomerId
    shipping_address: ShippingAddress
    order_created_at: datetime

@dataclass(frozen=True)
class OrderItemAddedEvent(DomainEvent):
    order_id: OrderId
    order_item_id: OrderItemId
    product_id: ProductId
    quantity: int
    price_per_unit: Money

@dataclass(frozen=True)
class OrderStatusChangedEvent(DomainEvent):
    order_id: OrderId
    old_status: OrderStatus
    new_status: OrderStatus

@dataclass(frozen=True)
class OrderTotalAmountRecalculatedEvent(DomainEvent):
    order_id: OrderId
    new_total_amount: Money

# --- Агрегат Order (из предыдущего модуля, с событиями) ---
class Order:
    order_id: OrderId
    customer_id: CustomerId
    _order_items: List[OrderItem]
    shipping_address: ShippingAddress
    status: OrderStatus
    created_at: datetime
    _updated_at: datetime
    _domain_events: List[DomainEvent]

    def __init__(
        self,
        order_id: OrderId,
        customer_id: CustomerId,
        shipping_address: ShippingAddress,
        created_at: Optional[datetime] = None,
    ):
        self.order_id = order_id
        self.customer_id = customer_id
        self._order_items = []
        self.shipping_address = shipping_address
        self.status = OrderStatus.PENDING
        self.created_at = created_at or datetime.now(timezone.utc)
        self._updated_at = self.created_at
        self._domain_events = []

        self._add_event(
            OrderCreatedEvent(
                order_id=self.order_id,
                customer_id=self.customer_id,
                shipping_address=self.shipping_address,
                order_created_at=self.created_at
            )
        )
        self._add_event(
            OrderTotalAmountRecalculatedEvent(
                order_id=self.order_id,
                new_total_amount=self.total_amount
            )
        )

    def _add_event(self, event: DomainEvent) -> None:
        self._domain_events.append(event)

    def get_uncommitted_events(self) -> List[DomainEvent]:
        return list(self._domain_events)

    def clear_uncommitted_events(self) -> None:
        self._domain_events.clear()

    @property
    def updated_at(self) -> datetime:
        return self._updated_at

    @property
    def order_items(self) -> Tuple[OrderItem, ...]:
        return tuple(self._order_items)

    @property
    def total_amount(self) -> Money:
        if not self._order_items:
            return Money.zero(self.shipping_address.country_code if hasattr(self.shipping_address, 'country_code') and self.shipping_address.country_code else "USD") # Пример
        currency = self._order_items[0].price_per_unit.currency
        total = Money.zero(currency)
        for item in self._order_items:
            total += item.calculate_item_total()
        return total

    def _mark_updated(self) -> None:
        self._updated_at = datetime.now(timezone.utc)

    def _recalculate_total_and_notify(self) -> None:
        self._mark_updated()
        self._add_event(
            OrderTotalAmountRecalculatedEvent(
                order_id=self.order_id,
                new_total_amount=self.total_amount
            )
        )

    def add_item(
        self,
        product_id: ProductId,
        quantity: int,
        price_per_unit: Money,
        order_item_id_val: Optional[OrderItemId] = None
    ) -> OrderItemId:
        if self.status not in [OrderStatus.PENDING]:
            raise ValueError(f"Cannot add item to order in status {self.status.value}")

        new_item_id = order_item_id_val or OrderItemId(uuid.uuid4())
        item = OrderItem(
            order_item_id=new_item_id,
            product_id=product_id,
            quantity=quantity,
            price_per_unit=price_per_unit,
        )
        self._order_items.append(item)
        self._add_event(
            OrderItemAddedEvent(
                order_id=self.order_id,
                order_item_id=item.order_item_id,
                product_id=item.product_id,
                quantity=item.quantity,
                price_per_unit=item.price_per_unit
            )
        )
        self._recalculate_total_and_notify()
        return new_item_id

    def _change_status(self, new_status: OrderStatus) -> None:
        old_status = self.status
        self.status = new_status
        self._mark_updated()
        self._add_event(
            OrderStatusChangedEvent(
                order_id=self.order_id,
                old_status=old_status,
                new_status=self.status
            )
        )

    def pay(self) -> None:
        if self.status != OrderStatus.PENDING:
            raise ValueError(f"Order can only be paid if status is PENDING. Current status: {self.status.value}")
        if not self._order_items:
            raise ValueError("Cannot pay for an empty order.")
        self._change_status(OrderStatus.PAID)

    # ... (другие методы Order: ship, deliver, cancel, remove_item, update_item_quantity, change_shipping_address)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Order):
            return NotImplemented
        return self.order_id == other.order_id

    def __hash__(self) -> int:
        return hash(self.order_id)

    def __repr__(self) -> str:
        return (f"<Order id={self.order_id} customer_id={self.customer_id} status='{self.status.value}' "
                f"items={len(self._order_items)} total={self.total_amount}>")


# --- Пользовательские исключения для Репозитория ---
class OrderRepositoryError(Exception):
    """Базовый класс для ошибок репозитория заказов."""
    pass

class OrderNotFoundError(OrderRepositoryError):
    """Заказ не найден в репозитории."""
    def __init__(self, order_id: OrderId):
        super().__init__(f"Order with ID {order_id} not found.")
        self.order_id = order_id

class OrderAlreadyExistsError(OrderRepositoryError):
    """Заказ с таким ID уже существует в репозитории."""
    def __init__(self, order_id: OrderId):
        super().__init__(f"Order with ID {order_id} already exists.")
        self.order_id = order_id


# --- Интерфейс Репозитория ---
class OrderRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, order: Order) -> None:
        """Добавляет новый заказ в репозиторий."""
        raise NotImplementedError

    @abc.abstractmethod
    def get_by_id(self, order_id: OrderId) -> Optional[Order]:
        """Получает заказ по его ID."""
        raise NotImplementedError

    @abc.abstractmethod
    def save(self, order: Order) -> None:
        """Сохраняет (обновляет) существующий заказ."""
        raise NotImplementedError

    @abc.abstractmethod
    def find_by_customer_id(self, customer_id: CustomerId) -> List[Order]:
        """Находит все заказы для указанного клиента."""
        raise NotImplementedError

    @abc.abstractmethod
    def delete(self, order_id: OrderId) -> None:
        """(Опционально) Удаляет заказ по ID."""
        raise NotImplementedError


# --- In-Memory Реализация Репозитория ---
class InMemoryOrderRepository(OrderRepository):
    def __init__(self):
        self._orders: Dict[OrderId, Order] = {}

    def add(self, order: Order) -> None:
        if order.order_id in self._orders:
            raise OrderAlreadyExistsError(order.order_id)
        # Сохраняем глубокую копию, чтобы избежать модификации объекта в репозитории извне
        self._orders[order.order_id] = copy.deepcopy(order)
        print(f"Repository: Order {order.order_id} added.")

    def get_by_id(self, order_id: OrderId) -> Optional[Order]:
        order = self._orders.get(order_id)
        if order:
            # Возвращаем глубокую копию
            print(f"Repository: Order {order_id} retrieved.")
            return copy.deepcopy(order)
        print(f"Repository: Order {order_id} not found for retrieval.")
        return None

    def save(self, order: Order) -> None:
        if order.order_id not in self._orders:
            raise OrderNotFoundError(order.order_id)
        # Сохраняем глубокую копию
        self._orders[order.order_id] = copy.deepcopy(order)
        print(f"Repository: Order {order.order_id} saved (updated).")

    def find_by_customer_id(self, customer_id: CustomerId) -> List[Order]:
        found_orders = [
            copy.deepcopy(order) for order in self._orders.values()
            if order.customer_id == customer_id
        ]
        print(f"Repository: Found {len(found_orders)} orders for customer {customer_id}.")
        return found_orders

    def delete(self, order_id: OrderId) -> None:
        if order_id not in self._orders:
            raise OrderNotFoundError(order_id)
        del self._orders[order_id]
        print(f"Repository: Order {order_id} deleted.")

    def list_all(self) -> List[Order]: # Вспомогательный метод для тестов
        return [copy.deepcopy(order) for order in self._orders.values()]


# --- Примеры использования / Простые тесты ---
if __name__ == "__main__":
    repo: OrderRepository = InMemoryOrderRepository()

    # Создаем тестовые данные
    cust_id1 = CustomerId(uuid.uuid4())
    cust_id2 = CustomerId(uuid.uuid4())

    addr1 = ShippingAddress(street="1 Main St", city="Testville", postal_code="12345", country="USA")
    addr2 = ShippingAddress(street="2 Other Ave", city="Sampleburg", postal_code="67890", country="USA")

    order1_id = OrderId(uuid.uuid4())
    order1 = Order(order_id=order1_id, customer_id=cust_id1, shipping_address=addr1)
    order1.add_item(ProductId(uuid.uuid4()), 2, Money(Decimal("10.00")))
    order1.add_item(ProductId(uuid.uuid4()), 1, Money(Decimal("25.50")))

    order2_id = OrderId(uuid.uuid4())
    order2 = Order(order_id=order2_id, customer_id=cust_id2, shipping_address=addr2)
    order2.add_item(ProductId(uuid.uuid4()), 5, Money(Decimal("5.00")))

    order3_id = OrderId(uuid.uuid4())
    order3 = Order(order_id=order3_id, customer_id=cust_id1, shipping_address=addr1) # Еще один заказ для cust_id1
    order3.add_item(ProductId(uuid.uuid4()), 1, Money(Decimal("100.00")))


    print("--- Тестирование Репозитория Заказов ---")

    # 1. Добавление заказов
    print("\n1. Добавление заказов:")
    try:
        repo.add(order1)
        repo.add(order2)
        repo.add(order3)
    except OrderRepositoryError as e:
        print(f"Ошибка при добавлении: {e}")

    # Попытка добавить существующий
    try:
        repo.add(order1) # Должно вызвать OrderAlreadyExistsError
    except OrderAlreadyExistsError as e:
        print(f"Ожидаемая ошибка: {e}")

    print(f"Всего заказов в репозитории: {len(repo.list_all())}")

    # 2. Получение заказа по ID
    print("\n2. Получение заказа по ID:")
    retrieved_order1 = repo.get_by_id(order1_id)
    if retrieved_order1:
        print(f"Получен заказ 1: {retrieved_order1}")
        print(f"  ID объекта в памяти: {id(retrieved_order1)}, ID исходного: {id(order1)}")
        assert retrieved_order1.order_id == order1_id
        assert retrieved_order1 is not order1 # Проверка, что это копия
    else:
        print(f"Заказ {order1_id} не найден.")

    non_existent_id = OrderId(uuid.uuid4())
    retrieved_non_existent = repo.get_by_id(non_existent_id)
    assert retrieved_non_existent is None
    print(f"Попытка получить несуществующий заказ ({non_existent_id}): {'Не найден' if retrieved_non_existent is None else 'Найден!'}")

    # 3. Обновление заказа
    print("\n3. Обновление заказа:")
    if retrieved_order1:
        retrieved_order1.pay() # Изменяем статус
        retrieved_order1.add_item(ProductId(uuid.uuid4()), 1, Money(Decimal("7.00"))) # Добавляем позицию
        try:
            repo.save(retrieved_order1)
            updated_order1_from_repo = repo.get_by_id(order1_id)
            if updated_order1_from_repo:
                print(f"Обновленный заказ 1 из репо: {updated_order1_from_repo}")
                assert updated_order1_from_repo.status == OrderStatus.PAID
                assert len(updated_order1_from_repo.order_items) == 3
        except OrderRepositoryError as e:
            print(f"Ошибка при сохранении: {e}")

    # Попытка обновить несуществующий
    fake_order_to_save = Order(OrderId(uuid.uuid4()), cust_id1, addr1)
    try:
        repo.save(fake_order_to_save)
    except OrderNotFoundError as e:
        print(f"Ожидаемая ошибка при сохранении несуществующего: {e}")


    # 4. Поиск заказов по ID клиента
    print("\n4. Поиск заказов по ID клиента:")
    orders_cust1 = repo.find_by_customer_id(cust_id1)
    print(f"Заказы для клиента {cust_id1}:")
    for o in orders_cust1:
        print(f"  - {o}")
    assert len(orders_cust1) == 2

    orders_cust2 = repo.find_by_customer_id(cust_id2)
    print(f"Заказы для клиента {cust_id2}:")
    for o in orders_cust2:
        print(f"  - {o}")
    assert len(orders_cust2) == 1

    non_existent_cust_id = CustomerId(uuid.uuid4())
    orders_non_existent_cust = repo.find_by_customer_id(non_existent_cust_id)
    assert len(orders_non_existent_cust) == 0
    print(f"Заказы для несуществующего клиента {non_existent_cust_id}: {len(orders_non_existent_cust)}")

    # 5. Удаление заказа (опционально)
    print("\n5. Удаление заказа:")
    try:
        repo.delete(order2_id)
        assert repo.get_by_id(order2_id) is None
        print(f"Заказ {order2_id} успешно удален.")
    except OrderRepositoryError as e:
        print(f"Ошибка при удалении: {e}")

    # Попытка удалить несуществующий
    try:
        repo.delete(order2_id) # Уже удален
    except OrderNotFoundError as e:
        print(f"Ожидаемая ошибка при удалении несуществующего: {e}")

    print(f"\nВсего заказов в репозитории после всех операций: {len(repo.list_all())}")
    for o in repo.list_all():
        print(o)
