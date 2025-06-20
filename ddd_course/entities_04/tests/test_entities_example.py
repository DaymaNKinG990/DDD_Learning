"""
Тесты для примеров из модуля "Сущности (Entities)".
"""

import uuid
from decimal import Decimal

import pytest

# Предполагается, что entities_example_02.py находится в ddd_course.entities_04
# Для корректного импорта может потребоваться настройка PYTHONPATH
# или запуск pytest из корневой директории проекта.
from ddd_course.entities_04.entities_example_02 import Product, User


# Тесты для базового класса Entity (через его потомков)
def test_entity_creation_has_id():
    """Тест: У созданной сущности есть ID."""
    user = User(username="testuser", email="test@example.com")
    assert hasattr(user, "id")
    assert isinstance(user.id, uuid.UUID)

    product = Product(
        name="Test Product", description="A test product.", price=Decimal("10.00")
    )
    assert hasattr(product, "id")
    assert isinstance(product.id, uuid.UUID)


def test_entity_equality_and_hash():
    """Тест: Сущности с одинаковым ID равны и имеют одинаковый хеш."""
    # Тестирование через User
    user_id = uuid.uuid4()
    user1 = User(username="user1", email="user1@example.com", user_id=user_id)
    user2 = User(
        username="user2", email="user2@example.com", user_id=user_id
    )  # Другие данные, тот же ID
    user3 = User(
        username="user3", email="user3@example.com"
    )  # Другой ID, сгенерированный автоматически

    assert user1.id == user_id
    assert user2.id == user_id
    assert user3.id is not None
    assert user1.id != user3.id

    assert user1 == user2, "Пользователи с одинаковым ID должны быть равны"
    assert user1 != user3, "Пользователи с разными ID не должны быть равны"
    assert hash(user1) == hash(
        user2
    ), "Хеши пользователей с одинаковым ID должны быть равны"

    # Тестирование через Product
    product_id = uuid.uuid4()
    prod1 = Product(
        name="P1", description="D1", price=Decimal("1.00"), product_id=product_id
    )
    prod2 = Product(
        name="P2", description="D2", price=Decimal("2.00"), product_id=product_id
    )
    prod3 = Product(name="P3", description="D3", price=Decimal("3.00"))  # Другой ID

    assert prod1.id == product_id
    assert prod2.id == product_id
    assert prod3.id is not None
    assert prod1.id != prod3.id

    assert prod1 == prod2, "Продукты с одинаковым ID должны быть равны"
    assert prod1 != prod3, "Продукты с разными ID не должны быть равны"
    assert hash(prod1) == hash(
        prod2
    ), "Хеши продуктов с одинаковым ID должны быть равны"

    # Проверка случая, когда один ID передан, другой сгенерирован
    user_with_id = User(
        username="u_id", email="uid@example.com", user_id=user_id
    )  # user_id определен выше
    user_auto_id = User(username="u_auto", email="uauto@example.com")  # ID генерируется
    assert user_with_id != user_auto_id
    assert user_with_id.id != user_auto_id.id


# Тесты для класса User
def test_user_creation_successful():
    """Тест: Успешное создание пользователя."""
    user = User(username="johndoe", email="john.doe@example.com")
    assert user.username == "johndoe"
    assert user.email == "john.doe@example.com"
    assert user.is_active is True
    assert isinstance(user.id, uuid.UUID)


def test_user_creation_empty_username():
    """Тест: Создание пользователя с пустым именем пользователя вызывает ValueError."""
    with pytest.raises(ValueError, match="Имя пользователя не может быть пустым."):
        User(username="", email="test@example.com")


def test_user_creation_invalid_email():
    """Тест: Создание пользователя с невалидным email вызывает ValueError."""
    with pytest.raises(ValueError, match="Некорректный формат email: invalid-email"):
        User(username="testuser", email="invalid-email")


def test_user_update_email_successful():
    """Тест: Успешное обновление email пользователя."""
    user = User(username="testuser", email="old@example.com")
    user.update_email("new@example.com")
    assert user.email == "new@example.com"


def test_user_update_email_invalid():
    """Тест: Обновление email на невалидный вызывает ValueError."""
    user = User(username="testuser", email="old@example.com")
    with pytest.raises(ValueError, match="Некорректный формат email: invalid-email"):
        user.update_email("invalid-email")


def test_user_activate_deactivate():
    """Тест: Активация и деактивация пользователя."""
    user = User(username="testuser", email="test@example.com")
    assert user.is_active is True

    user.deactivate()
    assert user.is_active is False

    user.activate()
    assert user.is_active is True


def test_user_repr():
    """Тест: Корректность строкового представления пользователя."""
    user_id_val = uuid.uuid4()
    user = User(username="testuser", email="test@example.com", user_id=user_id_val)
    expected_repr = (
        f"User(id={user_id_val!r}, username='testuser', "
        f"email='test@example.com', is_active=True)"
    )
    assert repr(user) == expected_repr


# Тесты для класса Product
def test_product_creation_successful():
    """Тест: Успешное создание продукта."""
    product = Product(
        name="Laptop", description="High-end laptop", price=Decimal("1200.50")
    )
    assert product.name == "Laptop"
    assert product.description == "High-end laptop"
    assert product.price == Decimal("1200.50")
    assert product.is_archived is False
    assert isinstance(product.id, uuid.UUID)


def test_product_creation_empty_name():
    """Тест: Создание продукта с пустым названием вызывает ValueError."""
    with pytest.raises(ValueError, match="Название продукта не может быть пустым."):
        Product(name="", description="Test desc", price=Decimal("10.00"))


def test_product_creation_negative_price():
    """Тест: Создание продукта с отрицательной ценой вызывает ValueError."""
    with pytest.raises(
        ValueError, match="Цена продукта не может быть отрицательной: -10.00"
    ):
        Product(name="Test Product", description="Test desc", price=Decimal("-10.00"))


def test_product_update_price_successful():
    """Тест: Успешное обновление цены продукта."""
    product = Product(
        name="Test Product", description="Test desc", price=Decimal("100.00")
    )
    product.update_price(Decimal("120.00"))
    assert product.price == Decimal("120.00")


def test_product_update_price_negative():
    """Тест: Обновление цены на отрицательную вызывает ValueError."""
    product = Product(
        name="Test Product", description="Test desc", price=Decimal("100.00")
    )
    with pytest.raises(
        ValueError, match="Цена продукта не может быть отрицательной: -50.00"
    ):
        product.update_price(Decimal("-50.00"))


def test_product_archive_unarchive():
    """Тест: Архивирование и разархивирование продукта."""
    product = Product(
        name="Test Product", description="Test desc", price=Decimal("10.00")
    )
    assert product.is_archived is False

    product.archive()
    assert product.is_archived is True

    product.unarchive()
    assert product.is_archived is False


def test_product_repr():
    """Тест: Корректность строкового представления продукта."""
    product_id_val = uuid.uuid4()
    product = Product(
        name="TestBook",
        description="A book",
        price=Decimal("29.99"),
        product_id=product_id_val,
    )
    expected_repr = (
        f"Product(id={product_id_val!r}, name='TestBook', "
        f"price=Decimal('29.99'), is_archived=False)"
    )
    assert repr(product) == expected_repr
