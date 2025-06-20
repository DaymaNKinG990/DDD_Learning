"""
Примеры кода для модуля "Агрегаты (Aggregates)".

Демонстрирует концепцию Агрегата на примере Заказа (Order) и его Позиций (OrderItem).
Order является корнем агрегата и отвечает за поддержание инвариантов.
"""

import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional


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

    product_id: ProductId
    product_name: str  # Имя продукта на момент добавления
    quantity: int
    price_per_unit: float  # Цена за единицу на момент добавления в заказ
    id: OrderItemId = field(default_factory=OrderItemId)

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

    customer_id: uuid.UUID  # ID покупателя
    id: OrderId = field(default_factory=OrderId)
    status: str = field(default=OrderStatus.PENDING)
    version: int = 1  # Для оптимистичной блокировки
    _items: List[OrderItem] = field(default_factory=list, init=False, repr=False)

    MAX_ITEMS_PER_ORDER = 10
    MAX_QUANTITY_PER_ITEM = 100

    @property
    def items(self) -> List[OrderItem]:
        return list(self._items)  # Возвращаем копию для защиты инкапсуляции

    def add_item(self, product: Product, quantity: int):
        if self.status != OrderStatus.PENDING:
            raise ValueError(
                f"Нельзя добавлять товары в заказ со статусом {self.status}."
            )
        if len(self._items) >= self.MAX_ITEMS_PER_ORDER:
            raise ValueError(
                f"Нельзя добавить больше {self.MAX_ITEMS_PER_ORDER} позиций в заказ."
            )
        if quantity <= 0 or quantity > self.MAX_QUANTITY_PER_ITEM:
            raise ValueError(
                f"Количество товара должно быть от 1 до {self.MAX_QUANTITY_PER_ITEM}."
            )

        # Проверяем, есть ли уже такой продукт в заказе
        for item in self._items:
            if item.product_id == product.id:
                # Если продукт уже есть, можно обновить количество или выбросить ошибку
                # В данном примере обновим количество, если это разрешено
                new_quantity = item.quantity + quantity
                if new_quantity > self.MAX_QUANTITY_PER_ITEM:
                    raise ValueError(
                        f"Общее количество товара {product.name} превысит лимит."
                    )
                item.change_quantity(new_quantity)
                self._increment_version()
                return

        order_item = OrderItem(
            product_id=product.id,
            product_name=product.name,
            quantity=quantity,
            price_per_unit=product.price,  # Фиксируем цену на момент добавления
        )
        self._items.append(order_item)
        self._increment_version()

    def remove_item(self, product_id: ProductId):
        if self.status != OrderStatus.PENDING:
            raise ValueError(
                f"Нельзя удалять товары из заказа со статусом {self.status}."
            )

        item_to_remove = self._find_item(product_id)
        if item_to_remove:
            self._items.remove(item_to_remove)
            self._increment_version()
        else:
            raise ValueError(f"Продукт с ID {product_id.value} не найден в заказе.")

    def update_item_quantity(self, product_id: ProductId, new_quantity: int):
        if self.status != OrderStatus.PENDING:
            raise ValueError(
                f"Нельзя изменять количество в заказе со статусом {self.status}."
            )
        if new_quantity <= 0 or new_quantity > self.MAX_QUANTITY_PER_ITEM:
            raise ValueError(
                (
                    "Новое количество товара должно быть от 1 до "
                    f"{self.MAX_QUANTITY_PER_ITEM}."
                )
            )

        item_to_update = self._find_item(product_id)
        if item_to_update:
            item_to_update.change_quantity(new_quantity)
            self._increment_version()
        else:
            raise ValueError(
                f"Продукт с ID {product_id.value} не найден для обновления."
            )

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


if __name__ == "__main__":
    # Создаем продукты (справочник)
    product_catalog: Dict[ProductId, Product] = {}
    p1_id = ProductId()
    p2_id = ProductId()
    p3_id = ProductId()

    product1 = Product(id=p1_id, name="Ноутбук 'Мощь'", price=75000.00)
    product2 = Product(id=p2_id, name="Мышь 'Скорость'", price=1500.00)
    product3 = Product(id=p3_id, name="Клавиатура 'Комфорт'", price=3000.00)
    product_catalog[p1_id] = product1
    product_catalog[p2_id] = product2
    product_catalog[p3_id] = product3

    print("--- Демонстрация Агрегата Order ---")

    # Создаем заказ
    customer_id = uuid.uuid4()
    order = Order(customer_id=customer_id)
    print(f"Создан заказ ID: {order.id.value} для клиента {customer_id}")
    print(
        f"Статус: {order.status}, Версия: {order.version}, "
        f"Сумма: {order.total_price:.2f}"
    )

    # Добавляем товары
    try:
        print("\nДобавляем товары...")
        order.add_item(product1, 1)  # Ноутбук
        print(
            f"Добавлен {product1.name}. Сумма: {order.total_price:.2f}, "
            f"Позиций: {len(order.items)}"
        )
        order.add_item(product2, 2)  # 2 Мыши
        print(
            f"Добавлены {product2.name} (2 шт). Сумма: {order.total_price:.2f}, "
            f"Позиций: {len(order.items)}"
        )
        order.add_item(product1, 1)  # Еще один ноутбук (обновит количество первого)
        print(
            f"Добавлен еще один {product1.name}. "
            f"Сумма: {order.total_price:.2f}, Позиций: {len(order.items)}"
        )
        print("Позиции в заказе:")
        for item in order.items:
            print(
                f" - {item.product_name}, кол-во: {item.quantity}, "
                f"цена: {item.price_per_unit:.2f}, сумма: {item.total_price:.2f}"
            )
        print(f"Версия заказа: {order.version}")
    except ValueError as e:
        print(f"Ошибка добавления: {e}")

    # Обновляем количество
    try:
        print("\nОбновляем количество мышей до 1...")
        order.update_item_quantity(product2.id, 1)
        print(f"Количество {product2.name} обновлено. Сумма: {order.total_price:.2f}")
        print(f"Версия заказа: {order.version}")
    except ValueError as e:
        print(f"Ошибка обновления: {e}")

    # Удаляем товар
    try:
        print("\nУдаляем клавиатуру (которой нет)...")
        order.remove_item(product3.id)  # Такой позиции нет
    except ValueError as e:
        print(f"Ошибка удаления: {e}")

    try:
        print("\nУдаляем мышь...")
        order.remove_item(product2.id)
        print(
            f"{product2.name} удалена. Сумма: {order.total_price:.2f}, "
            f"Позиций: {len(order.items)}"
        )
        print(f"Версия заказа: {order.version}")
    except ValueError as e:
        print(f"Ошибка удаления: {e}")

    # Попытка добавить слишком много позиций
    try:
        print("\nПытаемся добавить слишком много разных позиций...")
        for i in range(Order.MAX_ITEMS_PER_ORDER + 1):
            temp_prod_id = ProductId()
            temp_prod = Product(id=temp_prod_id, name=f"Тестовый товар {i}", price=10.0)
            order.add_item(temp_prod, 1)
    except ValueError as e:
        print(f"Ошибка: {e}")

    # Оплата заказа
    try:
        print("\nОплачиваем заказ...")
        order.pay()
        print(f"Статус заказа: {order.status}, Версия: {order.version}")
    except ValueError as e:
        print(f"Ошибка оплаты: {e}")

    # Попытка добавить товар в оплаченный заказ
    try:
        print("\nПытаемся добавить товар в оплаченный заказ...")
        order.add_item(product3, 1)
    except ValueError as e:
        print(f"Ошибка: {e}")

    # Отгрузка заказа
    try:
        print("\nОтгружаем заказ...")
        order.ship()
        print(f"Статус заказа: {order.status}, Версия: {order.version}")
    except ValueError as e:
        print(f"Ошибка отгрузки: {e}")

    # Отмена заказа (пример)
    # order_to_cancel = Order(customer_id=uuid.uuid4())
    # order_to_cancel.add_item(product1,1)
    # print(f"\nОтменяем заказ {order_to_cancel.id.value}...")
    # order_to_cancel.cancel()
    # print(f"Статус: {order_to_cancel.status}, Версия: {order_to_cancel.version}")

    # Демонстрация неизменяемости списка items при получении
    print("\nДемонстрация защиты списка items:")
    current_items = order.items
    print(f"Количество позиций до попытки изменения извне: {len(current_items)}")
    try:
        # Эта операция не должна повлиять на заказ, т.к. order.items возвращает копию
        current_items.append(
            OrderItem(
                product_id=product3.id,
                product_name="Хакерский товар",
                quantity=100,
                price_per_unit=1.0,
            )
        )
        print(
            f"Количество позиций в 'current_items' после добавления: "
            f"{len(current_items)}"
        )
        print(
            f"Количество позиций в заказе (order.items) после попытки: "
            f"{len(order.items)}"
        )
        assert len(order.items) != len(current_items), "Инвариант списка items нарушен!"
    except Exception as e:
        print(f"Произошла ошибка при попытке изменить список items: {e}")
