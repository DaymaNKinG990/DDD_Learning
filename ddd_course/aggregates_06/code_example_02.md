# Пример кода: Агрегат "Заказ"

Этот пример демонстрирует базовую реализацию агрегата на примере Заказа (`Order`) и его Позиций (`OrderItem`).

```python
"""
Примеры кода для модуля "Агрегаты (Aggregates)".

Демонстрирует концепцию Агрегата на примере Заказа (Order) и его Позиций (OrderItem).
Order является корнем агрегата и отвечает за поддержание инвариантов.
"""

import uuid
from dataclasses import dataclass, field
from typing import List, Optional, Dict


@dataclass(frozen=True)
class ProductId:
    """Идентификатор продукта (может быть VO)."""
    value: uuid.UUID = field(default_factory=uuid.uuid4)


@dataclass
class Product:
    """Продукт, на который ссылается позиция заказа. Вне агрегата Order.
       Для примера упрощен, может быть полноценной сущностью или VO.
    """
    id: ProductId
    name: str
    price: float  # Текущая цена продукта

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        if not isinstance(other, Product):
            return NotImplemented
        return self.id == other.id


@dataclass
class OrderItemId:
    """Идентификатор позиции заказа."""
    value: uuid.UUID = field(default_factory=uuid.uuid4)


@dataclass
class OrderItem:
    """Сущность "Позиция Заказа" внутри агрегата Order."""
    id: OrderItemId = field(default_factory=OrderItemId)
    product_id: ProductId
    product_name: str # Имя продукта на момент добавления
    quantity: int
    price_per_unit: float  # Цена за единицу на момент добавления в заказ

    def __post_init__(self):
        if self.quantity <= 0:
            raise ValueError("Количество должно быть положительным.")
        if self.price_per_unit < 0:
            raise ValueError("Цена за единицу не может быть отрицательной.")

    @property
    def total_price(self) -> float:
        return self.quantity * self.price_per_unit

    def change_quantity(self, new_quantity: int):
        """Изменение количества. Контролируется корнем агрегата."""
        if new_quantity <= 0:
            raise ValueError("Новое количество должно быть положительным.")
        self.quantity = new_quantity

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        if not isinstance(other, OrderItem):
            return NotImplemented
        return self.id == other.id


@dataclass
class OrderId:
    """Идентификатор заказа."""
    value: uuid.UUID = field(default_factory=uuid.uuid4)


class OrderStatus:
    """Статус заказа (может быть Enum)."""
    PENDING = "PENDING"
    PAID = "PAID"
    SHIPPED = "SHIPPED"
    CANCELLED = "CANCELLED"


@dataclass
class Order:
    """Агрегат "Заказ". Корень агрегата."""
    id: OrderId = field(default_factory=OrderId)
    customer_id: uuid.UUID # ID покупателя
    _items: List[OrderItem] = field(default_factory=list, init=False, repr=False)
    status: str = field(default=OrderStatus.PENDING)
    version: int = 1 # Для оптимистичной блокировки

    MAX_ITEMS_PER_ORDER = 10
    MAX_QUANTITY_PER_ITEM = 100

    @property
    def items(self) -> List[OrderItem]:
        return list(self._items) # Возвращаем копию для защиты инкапсуляции

    def add_item(self, product: Product, quantity: int):
        if self.status != OrderStatus.PENDING:
            raise ValueError(f"Нельзя добавлять товары в заказ со статусом {self.status}.")
        if len(self._items) >= self.MAX_ITEMS_PER_ORDER:
            raise ValueError(f"Нельзя добавить больше {self.MAX_ITEMS_PER_ORDER} позиций в заказ.")
        if quantity <= 0 or quantity > self.MAX_QUANTITY_PER_ITEM:
            raise ValueError(f"Количество товара должно быть от 1 до {self.MAX_QUANTITY_PER_ITEM}.")

        # Проверяем, есть ли уже такой продукт в заказе
        for item in self._items:
            if item.product_id == product.id:
                # Если продукт уже есть, можно обновить количество или выбросить ошибку
                # В данном примере обновим количество, если это разрешено
                new_quantity = item.quantity + quantity
                if new_quantity > self.MAX_QUANTITY_PER_ITEM:
                    raise ValueError(f"Общее количество товара {product.name} превысит лимит.")
                item.change_quantity(new_quantity)
                self._increment_version()
                return

        order_item = OrderItem(
            product_id=product.id,
            product_name=product.name,
            quantity=quantity,
            price_per_unit=product.price # Фиксируем цену на момент добавления
        )
        self._items.append(order_item)
        self._increment_version()

    def remove_item(self, product_id: ProductId):
        if self.status != OrderStatus.PENDING:
            raise ValueError(f"Нельзя удалять товары из заказа со статусом {self.status}.")

        item_to_remove = self._find_item(product_id)
        if item_to_remove:
            self._items.remove(item_to_remove)
            self._increment_version()
        else:
            raise ValueError(f"Продукт с ID {product_id.value} не найден в заказе.")

    def update_item_quantity(self, product_id: ProductId, new_quantity: int):
        if self.status != OrderStatus.PENDING:
            raise ValueError(f"Нельзя изменять количество в заказе со статусом {self.status}.")
        if new_quantity <= 0 or new_quantity > self.MAX_QUANTITY_PER_ITEM:
            raise ValueError(f"Новое количество товара должно быть от 1 до {self.MAX_QUANTITY_PER_ITEM}.")

        item_to_update = self._find_item(product_id)
        if item_to_update:
            item_to_update.change_quantity(new_quantity)
            self._increment_version()
        else:
            raise ValueError(f"Продукт с ID {product_id.value} не найден для обновления.")

    def _find_item(self, product_id: ProductId) -> Optional[OrderItem]:
        for item in self._items:
            if item.product_id == product_id:
                return item
        return None

    @property
    def total_price(self) -> float:
        return sum(item.total_price for item in self._items)

    def pay(self):
        if self.status != OrderStatus.PENDING:
            raise ValueError(f"Заказ не может быть оплачен в статусе {self.status}.")
        if not self._items:
            raise ValueError("Нельзя оплатить пустой заказ.")
        self.status = OrderStatus.PAID
        self._increment_version()
        print(f"Заказ {self.id.value} оплачен. Сумма: {self.total_price:.2f}")

    def ship(self):
        if self.status != OrderStatus.PAID:
            raise ValueError(f"Заказ не может быть отгружен в статусе {self.status}.")
        self.status = OrderStatus.SHIPPED
        self._increment_version()
        print(f"Заказ {self.id.value} отгружен.")

    def cancel(self):
        if self.status not in [OrderStatus.PENDING, OrderStatus.PAID]:
            raise ValueError(f"Заказ не может быть отменен в статусе {self.status}.")
        self.status = OrderStatus.CANCELLED
        self._increment_version()
        print(f"Заказ {self.id.value} отменен.")

    def _increment_version(self):
        self.version += 1

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        if not isinstance(other, Order):
            return NotImplemented
        return self.id == other.id
```
