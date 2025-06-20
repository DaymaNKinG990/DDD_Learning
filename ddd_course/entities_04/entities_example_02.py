"""
Примеры кода для модуля "Сущности (Entities)".
"""

import uuid
from collections.abc import Hashable
from decimal import Decimal
from typing import Generic, TypeVar

# Определение обобщенного типа для ID, чтобы можно было использовать разные типы ID
T_ID = TypeVar("T_ID", bound=Hashable)


class Entity(Generic[T_ID]):
    """
    Базовый класс для Сущностей.
    Определяет идентичность через _id и реализует сравнение по ID.
    """

    def __init__(self, entity_id: T_ID):
        if entity_id is None:  # Проверка на None, т.к. тип может быть любым
            raise ValueError("Entity ID cannot be None")
        self._id: T_ID = entity_id

    @property
    def id(self) -> T_ID:
        return self._id

    def __eq__(self, other: object) -> bool:
        if not isinstance(
            other, self.__class__
        ):  # Сравниваем только с объектами того же класса
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(id={self.id})>"


class User(Entity[uuid.UUID]):
    """
    Пример Сущности "Пользователь".
    """

    def __init__(self, user_id: uuid.UUID, username: str, email: str):
        super().__init__(user_id)
        if not username:
            raise ValueError("Username cannot be empty")
        if not email:  # Простая проверка, в реальности была бы сложнее
            raise ValueError("Email cannot be empty")

        self._username: str = username
        self._email: str = email
        self._is_active: bool = True

    @property
    def username(self) -> str:
        return self._username

    @property
    def email(self) -> str:
        return self._email

    @email.setter
    def email(self, new_email: str) -> None:
        # Здесь могут быть бизнес-правила для смены email
        if not new_email:  # Упрощенный пример
            raise ValueError("Email cannot be empty")
        # Предположим, есть проверка формата email
        if "@" not in new_email or "." not in new_email.split("@")[1]:
            raise ValueError("Invalid email format")
        self._email = new_email
        print(f"Email for user {self.id} changed to {new_email}")

    @property
    def is_active(self) -> bool:
        return self._is_active

    def activate(self) -> None:
        if self._is_active:
            print(f"User {self.id} is already active.")
            return
        self._is_active = True
        print(f"User {self.id} activated.")

    def deactivate(self) -> None:
        if not self._is_active:
            print(f"User {self.id} is already inactive.")
            return
        self._is_active = False
        print(f"User {self.id} deactivated.")

    def __repr__(self) -> str:
        return (
            f"<User(id={self.id}, username='{self.username}', "
            f"email='{self.email}', active={self.is_active})>"
        )


class Product(Entity[uuid.UUID]):
    """
    Пример Сущности "Продукт".
    """

    def __init__(
        self, product_id: uuid.UUID, name: str, price: Decimal, stock_quantity: int = 0
    ):
        super().__init__(product_id)
        if not name:
            raise ValueError("Product name cannot be empty.")
        if price <= Decimal("0"):
            raise ValueError("Price must be positive.")
        if stock_quantity < 0:
            raise ValueError("Stock quantity cannot be negative.")

        self._name: str = name
        self._price: Decimal = price
        self._stock_quantity: int = stock_quantity

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        if not value:
            raise ValueError("Product name cannot be empty.")
        self._name = value

    @property
    def price(self) -> Decimal:
        return self._price

    def update_price(self, new_price: Decimal) -> None:
        if new_price <= Decimal("0"):
            raise ValueError("Price must be positive.")
        self._price = new_price
        print(
            f"Price for product '{self.name}' (ID: {self.id}) updated to {self.price}"
        )

    @property
    def stock_quantity(self) -> int:
        return self._stock_quantity

    def add_stock(self, quantity: int) -> None:
        if quantity <= 0:
            raise ValueError("Quantity to add must be positive.")
        self._stock_quantity += quantity
        print(
            f"{quantity} units added to stock for '{self.name}'. "
            f"New stock: {self.stock_quantity}"
        )

    def remove_stock(self, quantity: int) -> None:
        if quantity <= 0:
            raise ValueError("Quantity to remove must be positive.")
        if self._stock_quantity < quantity:
            raise ValueError(
                f"Not enough stock for product '{self.name}'. "
                f"Requested: {quantity}, Available: {self.stock_quantity}"
            )
        self._stock_quantity -= quantity
        print(
            f"{quantity} units removed from stock for '{self.name}'. "
            f"New stock: {self.stock_quantity}"
        )

    def __repr__(self) -> str:
        return (
            f"<Product(id={self.id}, name='{self.name}', "
            f"price={self.price:.2f}, stock={self.stock_quantity})>"
        )


def main():
    """Основная функция для демонстрации работы с Сущностями."""
    print("--- Демонстрация Сущности User ---")
    user_id1 = uuid.uuid4()
    user1 = User(user_id=user_id1, username="john_doe", email="john.doe@example.com")
    print(user1)

    user1.email = "j.doe@newdomain.com"
    user1.deactivate()
    print(user1)

    user_id2 = uuid.uuid4()
    user2 = User(
        user_id=user_id2, username="jane_smith", email="jane.smith@example.com"
    )
    print(user2)

    # Сравнение сущностей
    user1_ref_same_id = User(
        user_id=user_id1, username="johnnyD", email="john@another.com"
    )
    print(f"user1 == user2: {user1 == user2}")  # False
    print(
        f"user1 == user1_ref_same_id: {user1 == user1_ref_same_id}"
    )  # True, т.к. ID совпадают

    print("\n--- Демонстрация Сущности Product ---")
    product_id1 = uuid.uuid4()
    product1 = Product(
        product_id=product_id1,
        name="Awesome Laptop",
        price=Decimal("1299.99"),
        stock_quantity=10,
    )
    print(product1)

    product1.update_price(Decimal("1249.00"))
    product1.add_stock(5)
    try:
        product1.remove_stock(20)
    except ValueError as e:
        print(f"Error: {e}")
    product1.remove_stock(12)
    print(product1)

    product_id2 = uuid.uuid4()
    product2 = Product(
        product_id=product_id2, name="Wireless Keyboard", price=Decimal("75.50")
    )
    print(product2)
    product2.add_stock(50)
    print(product2)

    # Проверка создания базовой сущности (если это нужно)
    # base_entity_id = 123 # Пример с int ID
    # base_entity = Entity[int](base_entity_id)
    # print(f"\nBase entity: {base_entity}")
    # another_base_entity = Entity[int](base_entity_id)
    # print(f"Base entities equal: {base_entity == another_base_entity}")


if __name__ == "__main__":
    main()
