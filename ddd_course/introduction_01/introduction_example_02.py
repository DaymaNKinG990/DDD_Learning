"""
Базовые примеры концепций DDD на Python.

Этот модуль демонстрирует основные концепции Domain-Driven Design
на простых примерах.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

# ============================================
# 1. Value Object (Объект-значение)
# ============================================


@dataclass(frozen=True)
class Email:
    """Пример объекта-значения: электронная почта.

    Атрибуты:
        address: Адрес электронной почты
    """

    address: str

    def __post_init__(self):
        # Простая валидация email. В реальных системах рекомендуется
        # использовать более строгую валидацию (например, с помощью
        # регулярных выражений или специализированных библиотек).
        if "@" not in self.address:
            raise ValueError("Некорректный email адрес")

    def __str__(self) -> str:
        return self.address


# ============================================
# 2. Entity (Сущность)
# ============================================


@dataclass
class User:
    """Пример сущности: пользователь.

    Атрибуты:
        id: Уникальный идентификатор пользователя
        email: Адрес электронной почты (объект-значение)
        name: Имя пользователя
        created_at: Дата и время создания
    """

    id: UUID
    email: Email
    name: str
    created_at: datetime

    def __post_init__(self):
        # Проверка инвариантов
        if not self.name.strip():
            raise ValueError("Имя пользователя не может быть пустым")

    def change_email(self, new_email: Email) -> None:
        """Изменить email пользователя.

        Аргументы:
            new_email: Новый адрес электронной почты
        """
        self.email = new_email


# ============================================
# 3. Aggregate (Агрегат)
# ============================================


@dataclass
class OrderItem:
    """Элемент заказа.

    Атрибуты:
        product_id: Идентификатор товара
        quantity: Количество
        price: Цена за единицу
    """

    product_id: UUID
    quantity: int
    price: float  # В реальных системах для денежных сумм лучше использовать
    # специальный объект-значение Money для избежания проблем с точностью float.


@dataclass
class Order:
    """Пример агрегата: заказ.

    Агрегат - это кластер доменных объектов, которые можно рассматривать
    как единое целое. Order является корнем агрегата (Aggregate Root).

    Атрибуты:
        id: Уникальный идентификатор заказа
        user_id: Идентификатор пользователя
        items: Список позиций заказа
        created_at: Дата и время создания
        status: Текущий статус заказа
    """

    id: UUID
    user_id: UUID
    items: List[OrderItem]
    created_at: datetime
    status: str = "created"

    def add_item(self, product_id: UUID, quantity: int, price: float) -> None:
        """Добавить товар в заказ.

        Аргументы:
            product_id: Идентификатор товара
            quantity: Количество
            price: Цена за единицу
        """
        if self.status != "created":
            raise ValueError("Невозможно изменить выполненный заказ")

        self.items.append(OrderItem(product_id, quantity, price))

    def calculate_total(self) -> float:
        """Рассчитать общую сумму заказа.

        Возвращает:
            Общая сумма заказа
        """
        return sum(item.quantity * item.price for item in self.items)

    def confirm(self) -> None:
        """Подтвердить заказ."""
        if not self.items:
            raise ValueError("Невозможно подтвердить пустой заказ")
        self.status = "confirmed"


# ============================================
# 4. Repository (Репозиторий, интерфейс)
# ============================================


class UserRepository:
    """Абстрактный репозиторий для работы с пользователями."""

    def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Найти пользователя по идентификатору."""
        raise NotImplementedError

    def get_by_email(self, email: Email) -> Optional[User]:
        """Найти пользователя по email."""
        raise NotImplementedError

    def add(self, user: User) -> None:
        """Добавить нового пользователя."""
        raise NotImplementedError

    def update(self, user: User) -> None:
        """Обновить данные пользователя."""
        raise NotImplementedError


# ============================================
# 5. Domain Service (Доменный сервис)
# ============================================


class UserRegistrationService:
    """Сервис для регистрации новых пользователей."""

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def register_user(self, email_address: str, name: str) -> User:
        """Зарегистрировать нового пользователя.

        Аргументы:
            email_address: Адрес электронной почты
            name: Имя пользователя

        Возвращает:
            Созданный пользователь

        Исключения:
            ValueError: Если пользователь с таким email уже существует
        """
        email = Email(email_address)

        # Проверяем, нет ли уже пользователя с таким email
        if self.user_repository.get_by_email(email) is not None:
            raise ValueError("Пользователь с таким email уже существует")

        # Создаем нового пользователя
        user = User(id=uuid4(), email=email, name=name, created_at=datetime.now())

        # Сохраняем пользователя
        self.user_repository.add(user)

        return user


# ============================================
# Пример использования
# ============================================

if __name__ == "__main__":
    # Создаем моковый репозиторий для демонстрации
    class InMemoryUserRepository(UserRepository):
        def __init__(self):
            self.users = {}

        def get_by_id(self, user_id):
            return self.users.get(str(user_id))

        def get_by_email(self, email):
            # В реальном репозитории здесь был бы эффективный запрос к БД.
            # Итерация по всем записям неэффективна для больших объемов данных.
            for user in self.users.values():
                if user.email == email:
                    return user
            return None

        def add(self, user):
            self.users[str(user.id)] = user

        def update(self, user):
            self.users[str(user.id)] = user

    # Демонстрация работы
    print("=== Демонстрация DDD концепций ===\n")

    # 1. Создаем репозиторий и сервис
    user_repo = InMemoryUserRepository()
    registration_service = UserRegistrationService(user_repo)

    # 2. Регистрируем нового пользователя
    try:
        user = registration_service.register_user(
            email_address="user@example.com", name="Иван Иванов"
        )
        print(f"Создан пользователь: {user.name} ({user.email})")

        # 3. Создаем заказ
        order = Order(id=uuid4(), user_id=user.id, items=[], created_at=datetime.now())

        # 4. Добавляем товары в заказ
        order.add_item(product_id=uuid4(), quantity=2, price=100.0)
        order.add_item(product_id=uuid4(), quantity=1, price=200.0)

        # 5. Подтверждаем заказ
        order.confirm()

        print(f"Создан заказ #{order.id} на сумму {order.calculate_total()} руб.")
        print(f"Статус заказа: {order.status}")

    except ValueError as e:
        print(f"Ошибка: {e}")
