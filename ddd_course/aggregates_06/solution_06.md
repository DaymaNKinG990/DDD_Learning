# Решение упражнения по модулю "Агрегаты (Aggregates)"

## Задание: Разработка Агрегата `Order` (Заказ)

Ниже представлен пример реализации Агрегата `Order` и связанных с ним классов на Python в соответствии с требованиями упражнения.

### Код решения

```python
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import List, NewType, Optional, Type, TypeVar

# Типы ID для большей ясности
OrderId = NewType("OrderId", uuid.UUID)
OrderItemId = NewType("OrderItemId", uuid.UUID)
CustomerId = NewType("CustomerId", uuid.UUID)
ProductId = NewType("ProductId", uuid.UUID)

_TMoney = TypeVar("_TMoney", bound="Money")
_TOrder = TypeVar("_TOrder", bound="Order")


@dataclass(frozen=True)
class Money:
    """
    Объект-значение для представления денежной суммы.
    Неизменяемый.
    """
    amount: Decimal
    currency: str = "USD"  # Валюта по умолчанию

    def __post_init__(self):
        if self.amount < Decimal(0):
            raise ValueError("Amount cannot be negative.")
        if not self.currency or len(self.currency) != 3:
            raise ValueError("Currency must be a 3-letter code.")

    def __add__(self: _TMoney, other: _TMoney) -> _TMoney:
        if not isinstance(other, Money):
            return NotImplemented
        if self.currency != other.currency:
            raise ValueError("Cannot add Money with different currencies.")
        return self.__class__(self.amount + other.amount, self.currency)

    def __sub__(self: _TMoney, other: _TMoney) -> _TMoney:
        if not isinstance(other, Money):
            return NotImplemented
        if self.currency != other.currency:
            raise ValueError("Cannot subtract Money with different currencies.")
        return self.__class__(self.amount - other.amount, self.currency)

    def __mul__(self: _TMoney, multiplier: int | Decimal) -> _TMoney:
        if not isinstance(multiplier, (int, Decimal)):
            return NotImplemented
        if multiplier < 0:
            raise ValueError("Multiplier cannot be negative.")
        return self.__class__(self.amount * Decimal(multiplier), self.currency)

    def __lt__(self, other: _TMoney) -> bool:
        if not isinstance(other, Money) or self.currency != other.currency:
            return NotImplemented
        return self.amount < other.amount

    def __le__(self, other: _TMoney) -> bool:
        if not isinstance(other, Money) or self.currency != other.currency:
            return NotImplemented
        return self.amount <= other.amount

    def __gt__(self, other: _TMoney) -> bool:
        if not isinstance(other, Money) or self.currency != other.currency:
            return NotImplemented
        return self.amount > other.amount

    def __ge__(self: _TMoney, other: _TMoney) -> bool:
        if not isinstance(other, Money) or self.currency != other.currency:
            return NotImplemented
        return self.amount >= other.amount

    @classmethod
    def zero(cls: Type[_TMoney], currency: str = "USD") -> _TMoney:
        return cls(Decimal(0), currency)


@dataclass(frozen=True)
class ShippingAddress:
    """
    Объект-значение для адреса доставки.
    Неизменяемый.
    """
    street: str
    city: str
    postal_code: str
    country: str

    def __post_init__(self):
        if not all([self.street, self.city, self.postal_code, self.country]):
            raise ValueError("All address fields must be provided.")


class OrderStatus(Enum):
    """Статусы заказа."""
    PENDING = "pending"
    PAID = "paid"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


@dataclass
class OrderItem:
    """
    Внутренняя сущность Агрегата Order, представляющая позицию заказа.
    """
    order_item_id: OrderItemId
    product_id: ProductId
    quantity: int
    price_per_unit: Money # Цена на момент добавления товара

    def __post_init__(self):
        if self.quantity <= 0:
            raise ValueError("Quantity must be positive.")

    def calculate_item_total(self) -> Money:
        """Рассчитывает общую стоимость для данной позиции заказа."""
        return self.price_per_unit * self.quantity

    # Методы изменения состояния OrderItem должны вызываться только из Order
    def _update_quantity(self, new_quantity: int) -> None:
        if new_quantity <= 0:
            raise ValueError("New quantity must be positive.")
        self.quantity = new_quantity


class Order:
    """
    Корень Агрегата "Заказ".
    """
    order_id: OrderId
    customer_id: CustomerId
    _order_items: List[OrderItem] # Приватный список для контроля доступа
    shipping_address: ShippingAddress
    status: OrderStatus
    created_at: datetime
    _updated_at: datetime # Приватное поле для контроля обновления

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
        self.created_at = created_at or datetime.utcnow()
        self._updated_at = self.created_at

    @property
    def updated_at(self) -> datetime:
        return self._updated_at

    @property
    def order_items(self) -> Tuple[OrderItem, ...]:
        """Предоставляет копию списка позиций заказа для чтения."""
        return tuple(self._order_items)

    @property
    def total_amount(self) -> Money:
        """Рассчитывает общую сумму заказа."""
        if not self._order_items:
            # Определяем валюту по первой позиции или используем стандартную
            # В реальном приложении валюта заказа может быть задана явно
            default_currency = "USD"
            return Money.zero(default_currency)

        # Предполагаем, что все позиции заказа имеют одинаковую валюту
        # Это должно обеспечиваться при добавлении позиций
        currency = self._order_items[0].price_per_unit.currency
        total = Money.zero(currency)
        for item in self._order_items:
            total += item.calculate_item_total()
        return total

    def _mark_updated(self) -> None:
        self._updated_at = datetime.utcnow()

    def add_item(
        self,
        product_id: ProductId,
        quantity: int,
        price_per_unit: Money,
        order_item_id: Optional[OrderItemId] = None
    ) -> OrderItemId:
        """Добавляет позицию в заказ."""
        if self.status not in [OrderStatus.PENDING]:
            raise ValueError(f"Cannot add item to order in status {self.status.value}")
        if quantity <= 0:
            raise ValueError("Quantity must be positive.")

        # Проверка на совпадение валюты
        if self._order_items and self._order_items[0].price_per_unit.currency != price_per_unit.currency:
            raise ValueError("Cannot add item with different currency to the order.")


        # Для упрощения, каждая позиция уникальна по order_item_id.
        # Если нужно объединять одинаковые product_id, логика будет сложнее.
        new_item_id = order_item_id or OrderItemId(uuid.uuid4())
        item = OrderItem(
            order_item_id=new_item_id,
            product_id=product_id,
            quantity=quantity,
            price_per_unit=price_per_unit,
        )
        self._order_items.append(item)
        self._mark_updated()
        return new_item_id

    def remove_item(self, order_item_id: OrderItemId) -> None:
        """Удаляет позицию из заказа."""
        if self.status not in [OrderStatus.PENDING]:
            raise ValueError(f"Cannot remove item from order in status {self.status.value}")

        item_to_remove = next((item for item in self._order_items if item.order_item_id == order_item_id), None)
        if not item_to_remove:
            raise ValueError(f"OrderItem with id {order_item_id} not found in order.")

        self._order_items.remove(item_to_remove)
        self._mark_updated()

    def update_item_quantity(self, order_item_id: OrderItemId, new_quantity: int) -> None:
        """Обновляет количество товара в позиции заказа."""
        if self.status not in [OrderStatus.PENDING]:
            raise ValueError(f"Cannot update item quantity in order with status {self.status.value}")
        if new_quantity <= 0:
            # Если количество 0, можно либо удалить позицию, либо выбросить ошибку
            # В данном случае, для соответствия ТЗ OrderItem, выбрасываем ошибку.
            # Для удаления используйте remove_item.
            raise ValueError("New quantity must be positive. To remove an item, use remove_item().")

        item_to_update = next((item for item in self._order_items if item.order_item_id == order_item_id), None)
        if not item_to_update:
            raise ValueError(f"OrderItem with id {order_item_id} not found in order.")

        item_to_update._update_quantity(new_quantity) # Используем "приватный" метод OrderItem
        self._mark_updated()

    def change_shipping_address(self, new_address: ShippingAddress) -> None:
        """Изменяет адрес доставки."""
        if self.status in [OrderStatus.SHIPPED, OrderStatus.DELIVERED, OrderStatus.CANCELLED]:
            raise ValueError(f"Cannot change shipping address for order in status {self.status.value}")
        self.shipping_address = new_address
        self._mark_updated()

    def pay(self) -> None:
        """Отмечает заказ как оплаченный."""
        if self.status != OrderStatus.PENDING:
            raise ValueError(f"Order can only be paid if status is PENDING. Current status: {self.status.value}")
        if not self._order_items:
            raise ValueError("Cannot pay for an empty order.")
        self.status = OrderStatus.PAID
        self._mark_updated()
        # Здесь можно было бы опубликовать событие OrderPaid

    def ship(self) -> None:
        """Отмечает заказ как отправленный."""
        if self.status != OrderStatus.PAID:
            raise ValueError(f"Order can only be shipped if status is PAID. Current status: {self.status.value}")
        self.status = OrderStatus.SHIPPED
        self._mark_updated()
        # Здесь можно было бы опубликовать событие OrderShipped

    def deliver(self) -> None:
        """Отмечает заказ как доставленный."""
        if self.status != OrderStatus.SHIPPED:
            raise ValueError(f"Order can only be delivered if status is SHIPPED. Current status: {self.status.value}")
        self.status = OrderStatus.DELIVERED
        self._mark_updated()

    def cancel(self) -> None:
        """Отменяет заказ."""
        if self.status in [OrderStatus.DELIVERED, OrderStatus.CANCELLED]:
            raise ValueError(f"Order cannot be cancelled if status is {self.status.value}")
        self.status = OrderStatus.CANCELLED
        self._mark_updated()
        # Здесь можно было бы опубликовать событие OrderCancelled

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Order):
            return NotImplemented
        return self.order_id == other.order_id

    def __hash__(self) -> int:
        return hash(self.order_id)

    def __repr__(self) -> str:
        return (f"<Order id={self.order_id} status='{self.status.value}' "
                f"items={len(self._order_items)} total={self.total_amount}>")


# Примеры использования:
if __name__ == "__main__":
    # Создание ID
    customer1_id = CustomerId(uuid.uuid4())
    product1_id = ProductId(uuid.uuid4())
    product2_id = ProductId(uuid.uuid4())

    # Создание Объектов-значений
    addr = ShippingAddress(street="123 Main St", city="Anytown", postal_code="12345", country="USA")
    price_p1 = Money(Decimal("19.99"), "USD")
    price_p2 = Money(Decimal("5.50"), "USD")

    print("--- Creating Order ---")
    order = Order(OrderId(uuid.uuid4()), customer1_id, addr)
    print(order)
    print(f"Initial total: {order.total_amount}")

    print("\n--- Adding Items ---")
    try:
        item1_id = order.add_item(product1_id, 2, price_p1)
        print(f"Added item 1: {item1_id}. Order: {order}")
        item2_id = order.add_item(product2_id, 1, price_p2)
        print(f"Added item 2: {item2_id}. Order: {order}")
        print(f"Order items: {order.order_items}")
        print(f"Total after adding items: {order.total_amount}")

        # Попытка добавить товар с отрицательным количеством
        # order.add_item(ProductId(uuid.uuid4()), -1, Money(Decimal("10.0")))
    except ValueError as e:
        print(f"Error adding item: {e}")

    print("\n--- Updating Item Quantity ---")
    try:
        order.update_item_quantity(item1_id, 3)
        print(f"Updated item 1 quantity. Order: {order}")
        print(f"Total after update: {order.total_amount}")
        # Попытка обновить несуществующий item
        # order.update_item_quantity(OrderItemId(uuid.uuid4()), 1)
    except ValueError as e:
        print(f"Error updating quantity: {e}")


    print("\n--- Removing Item ---")
    try:
        order.remove_item(item2_id)
        print(f"Removed item 2. Order: {order}")
        print(f"Total after removal: {order.total_amount}")
    except ValueError as e:
        print(f"Error removing item: {e}")

    print("\n--- Changing Shipping Address ---")
    new_addr = ShippingAddress("456 Oak Ave", "Otherville", "67890", "USA")
    try:
        order.change_shipping_address(new_addr)
        print(f"Changed shipping address. Order shipping address: {order.shipping_address}")
    except ValueError as e:
        print(f"Error changing address: {e}")


    print("\n--- Order Lifecycle ---")
    try:
        print(f"Order status: {order.status}")
        order.pay()
        print(f"Order status after pay: {order.status}")
        order.ship()
        print(f"Order status after ship: {order.status}")

        # Попытка изменить адрес после отправки
        # order.change_shipping_address(addr)

        order.deliver()
        print(f"Order status after deliver: {order.status}")

        # Попытка отменить доставленный заказ
        # order.cancel()
    except ValueError as e:
        print(f"Error in order lifecycle: {e}")

    print("\n--- Cancelling an Order ---")
    order2 = Order(OrderId(uuid.uuid4()), customer1_id, addr)
    item3_id = order2.add_item(product1_id, 1, price_p1)
    print(f"New order for cancellation: {order2}")
    try:
        order2.cancel()
        print(f"Order 2 status after cancel: {order2.status}")
    except ValueError as e:
        print(f"Error cancelling order: {e}")

    print("\n--- Money Object ---")
    m1 = Money(Decimal("10.00"))
    m2 = Money(Decimal("5.50"))
    m3 = Money(Decimal("10.00"))
    print(f"{m1} + {m2} = {m1 + m2}")
    print(f"{m1} * 3 = {m1 * 3}")
    print(f"{m1} == {m3}: {m1 == m3}") # True
    print(f"{m1} == {m2}: {m1 == m2}") # False
    money_set = {m1, m2, m3}
    print(f"Set of money objects: {money_set}") # Should contain 2 unique Money objects

    try:
        # Money("10", "US") # ValueError: Currency must be a 3-letter code.
        # Money("-5", "USD") # ValueError: Amount cannot be negative.
        m_eur = Money(Decimal("10"), "EUR")
        # print(m1 + m_eur) # ValueError: Cannot add Money with different currencies.
        pass
    except ValueError as e:
        print(f"Error with Money object: {e}")
