"""
Решение упражнения из модуля "Сущности (Entities)".
Разработка Сущности OrderItem.
"""

import uuid
from decimal import Decimal, InvalidOperation
from typing import Generic, Optional, TypeVar

# Определение обобщенного типа для ID, чтобы Entity мог быть более гибким,
# но для данного курса мы в основном используем UUID.
ID = TypeVar("ID", bound=uuid.UUID)


class Entity(Generic[ID]):
    """
    Базовый класс для всех Сущностей.

    Атрибуты:
        id (ID): Уникальный идентификатор сущности.
    """

    _id: ID

    def __init__(self, entity_id: Optional[ID] = None) -> None:
        """
        Инициализирует Сущность.

        Если entity_id не предоставлен, генерируется новый UUID.

        Args:
            entity_id (Optional[ID]): Уникальный идентификатор сущности.
                                       По умолчанию None, генерируется новый UUID.
        """
        # Мы используем type: ignore, так как mypy может не понять,
        # что ID будет конкретизирован как uuid.UUID в дочерних классах,
        # и uuid.uuid4() может не соответствовать обобщенному ID.
        # В данном контексте это безопасно, так как мы ожидаем UUID.
        self._id = entity_id if entity_id is not None else uuid.uuid4()  # type: ignore

    @property
    def id(self) -> ID:
        """Возвращает уникальный идентификатор сущности."""
        return self._id

    def __eq__(self, other: object) -> bool:
        """
        Сравнивает две сущности на равенство.
        Сущности равны, если они одного типа и их идентификаторы равны.
        """
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self._id == other._id

    def __hash__(self) -> int:
        """
        Возвращает хеш сущности, основанный на ее идентификаторе.
        """
        return hash(self._id)

    def __repr__(self) -> str:
        """
        Возвращает строковое представление сущности.
        """
        return f"{self.__class__.__name__}(id={self._id!r})"


class OrderItem(Entity[uuid.UUID]):
    """
    Сущность "Позиция Заказа".

    Представляет одну позицию (товар) в заказе клиента.

    Атрибуты:
        product_id (uuid.UUID): Идентификатор товара.
        quantity (int): Количество единиц товара.
        price_at_purchase (Decimal): Цена за единицу товара на момент покупки.
    """

    _product_id: uuid.UUID
    _quantity: int
    _price_at_purchase: Decimal

    def __init__(
        self,
        product_id: uuid.UUID,
        quantity: int,
        price_at_purchase: Decimal,
        order_item_id: Optional[uuid.UUID] = None,
    ) -> None:
        """
        Инициализирует позицию заказа.

        Args:
            product_id: Идентификатор товара.
            quantity: Количество товара.
            price_at_purchase: Цена за единицу товара на момент покупки.
            order_item_id: Уникальный идентификатор позиции заказа.
                           Если None, генерируется автоматически.

        Raises:
            TypeError: Если product_id не UUID, quantity не int,
                       или price_at_purchase не Decimal.
            ValueError: Если quantity не положительное число,
                        или price_at_purchase не положительное число.
        """
        super().__init__(entity_id=order_item_id)

        if not isinstance(product_id, uuid.UUID):
            raise TypeError("product_id должен быть типа UUID.")
        self._product_id = product_id

        if not isinstance(quantity, int):
            raise TypeError("quantity должно быть целым числом.")
        if quantity <= 0:
            raise ValueError(f"Количество товара должно быть положительным: {quantity}")
        self._quantity = quantity

        if not isinstance(price_at_purchase, Decimal):
            # Попытка конвертации, если это строка или число, которое может быть Decimal
            try:
                price_at_purchase = Decimal(str(price_at_purchase))
            except InvalidOperation:
                raise TypeError(
                    "price_at_purchase должно быть Decimal или строкой/числом, "
                    "конвертируемым в Decimal."
                )
        if price_at_purchase <= Decimal("0"):
            raise ValueError(
                "Цена товара на момент покупки должна быть положительной: "
                f"{price_at_purchase}"
            )
        self._price_at_purchase = price_at_purchase

    @property
    def product_id(self) -> uuid.UUID:
        """Возвращает идентификатор товара."""
        return self._product_id

    @property
    def quantity(self) -> int:
        """Возвращает количество товара."""
        return self._quantity

    @property
    def price_at_purchase(self) -> Decimal:
        """Возвращает цену за единицу товара на момент покупки."""
        return self._price_at_purchase

    def get_total_price(self) -> Decimal:
        """
        Рассчитывает и возвращает общую стоимость данной позиции заказа.

        Returns:
            Decimal: Общая стоимость (quantity * price_at_purchase).
        """
        return self._quantity * self._price_at_purchase

    def update_quantity(self, new_quantity: int) -> None:
        """
        Обновляет количество товара в позиции.

        Args:
            new_quantity: Новое количество товара.

        Raises:
            TypeError: Если new_quantity не int.
            ValueError: Если new_quantity не положительное число.
        """
        if not isinstance(new_quantity, int):
            raise TypeError("Новое количество должно быть целым числом.")
        if new_quantity <= 0:
            raise ValueError(
                f"Новое количество товара должно быть положительным: {new_quantity}"
            )
        self._quantity = new_quantity

    def __repr__(self) -> str:
        """
        Возвращает строковое представление объекта OrderItem.
        """
        return (
            f"{self.__class__.__name__}(id={self.id!r}, "
            f"product_id={self.product_id!r}, "
            f"quantity={self.quantity}, price_at_purchase={self.price_at_purchase!r})"
        )


def main_demonstration():
    """
    Демонстрация создания и использования Сущности OrderItem.
    """
    print("--- Демонстрация OrderItem ---")

    # 1. Создание нескольких экземпляров OrderItem
    product1_id = uuid.uuid4()
    product2_id = uuid.uuid4()

    try:
        item1 = OrderItem(
            product_id=product1_id, quantity=2, price_at_purchase=Decimal("199.99")
        )
        item2_id = uuid.uuid4()
        item2 = OrderItem(
            product_id=product2_id,
            quantity=1,
            price_at_purchase=Decimal("49.50"),
            order_item_id=item2_id,
        )
        # Создаем еще один экземпляр с тем же ID, что и item2, но другими данными
        # Это для демонстрации сравнения по ID
        item3_same_id_as_item2 = OrderItem(
            product_id=product1_id,  # Другой продукт
            quantity=10,  # Другое количество
            price_at_purchase=Decimal("10.00"),  # Другая цена
            order_item_id=item2_id,  # Тот же ID, что и у item2
        )
        item4_different_id = OrderItem(
            product_id=product2_id, quantity=3, price_at_purchase=Decimal("49.50")
        )

        print(f"Создана позиция 1: {item1}")
        print(f"Создана позиция 2: {item2}")
        print(f"Создана позиция 3 (тот же ID, что и у item2): {item3_same_id_as_item2}")
        print(f"Создана позиция 4 (другой ID): {item4_different_id}")

    except (ValueError, TypeError) as e:
        print(f"Ошибка при создании OrderItem: {e}")
        return  # Прекращаем демонстрацию, если базовая инициализация не удалась

    # 2. Демонстрация использования методов get_total_price() и update_quantity()
    print(f"\nОбщая стоимость для item1: {item1.get_total_price()}")
    print(f"Общая стоимость для item2: {item2.get_total_price()}")

    print(f"\nОбновляем количество для item1 с {item1.quantity} до 5...")
    try:
        item1.update_quantity(5)
        print(f"Новое количество для item1: {item1.quantity}")
        print(f"Новая общая стоимость для item1: {item1.get_total_price()}")
    except (ValueError, TypeError) as e:
        print(f"Ошибка при обновлении количества: {e}")

    print("\nПопытка обновить количество на некорректное значение (0)...")
    try:
        item1.update_quantity(0)
    except ValueError as e:
        print(f"Ожидаемая ошибка: {e}")

    # 3. Проверка корректности сравнения
    print("\n--- Проверка сравнения OrderItem ---")
    print(f"item2 (ID: {item2.id})")
    print(f"item3_same_id_as_item2 (ID: {item3_same_id_as_item2.id})")
    print(f"item4_different_id (ID: {item4_different_id.id})")

    # Сравнение объектов с одинаковым ID
    are_item2_and_item3_equal = item2 == item3_same_id_as_item2
    print(
        f"item2 == item3_same_id_as_item2 (одинаковые ID): {are_item2_and_item3_equal}"
    )
    assert are_item2_and_item3_equal, "Объекты с одинаковым ID должны быть равны"

    # Сравнение объектов с разными ID
    are_item2_and_item4_equal = item2 == item4_different_id
    print(f"item2 == item4_different_id (разные ID): {are_item2_and_item4_equal}")
    assert not are_item2_and_item4_equal, "Объекты с разными ID не должны быть равны"

    # Проверка хешей
    hash_item2 = hash(item2)
    hash_item3 = hash(item3_same_id_as_item2)
    hash_item4 = hash(item4_different_id)
    print(f"hash(item2): {hash_item2}")
    print(f"hash(item3_same_id_as_item2): {hash_item3}")
    print(f"hash(item4_different_id): {hash_item4}")
    assert hash_item2 == hash_item3, "Хеши объектов с одинаковым ID должны быть равны"
    assert (
        hash_item2 != hash_item4
    ), "Хеши объектов с разными ID не должны быть равны (вероятностно)"

    print("\n--- Демонстрация невалидных созданий ---")
    try:
        print("Попытка создать OrderItem с quantity=0:")
        OrderItem(product_id=uuid.uuid4(), quantity=0, price_at_purchase=Decimal("10"))
    except ValueError as e:
        print(f"  Ожидаемая ошибка: {e}")

    try:
        print("Попытка создать OrderItem с price_at_purchase=-5:")
        OrderItem(product_id=uuid.uuid4(), quantity=1, price_at_purchase=Decimal("-5"))
    except ValueError as e:
        print(f"  Ожидаемая ошибка: {e}")

    try:
        print("Попытка создать OrderItem с quantity='abc':")
        OrderItem(
            product_id=uuid.uuid4(), quantity="abc", price_at_purchase=Decimal("10")
        )  # type: ignore
    except TypeError as e:
        print(f"  Ожидаемая ошибка: {e}")

    print("\nДемонстрация завершена.")


if __name__ == "__main__":
    main_demonstration()
