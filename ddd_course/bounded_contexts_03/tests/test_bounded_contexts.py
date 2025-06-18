"""
Тесты для примера ограниченных контекстов.
"""
import pytest
from datetime import datetime
from uuid import uuid4

# Импортируем классы из примера
from ..bounded_contexts_example_02 import (
    Money, Product, Order, OrderItem, OrderStatus,
    Payment, PaymentStatus, OrderRepository, ProductRepository, PaymentService
)


# Фикстуры для тестирования

@pytest.fixture
def sample_products():
    """Создает тестовые товары."""
    return [
        Product(
            id=uuid4(),
            name="Ноутбук",
            description="Мощный игровой ноутбук",
            price=Money(150000),
            category="Электроника",
            stock_quantity=10
        ),
        Product(
            id=uuid4(),
            name="Смартфон",
            description="Флагманский смартфон",
            price=Money(120000),
            category="Электроника",
            stock_quantity=20
        )
    ]


@pytest.fixture
def order_repository_with_products(sample_products):
    """Создает репозиторий заказов с тестовыми товарами."""
    product_repo = ProductRepository()
    for product in sample_products:
        product_repo.save(product)
    
    order_repo = OrderRepository()
    return order_repo, product_repo


# Тесты для модели Product

def test_create_product():
    """Тест создания товара."""
    product = Product(
        id=uuid4(),
        name="Тестовый товар",
        description="Описание тестового товара",
        price=Money(1000),
        category="Тестовая категория",
        stock_quantity=5
    )
    
    assert product.name == "Тестовый товар"
    assert product.price.amount == 1000
    assert product.is_active is True


# Тесты для модели Order

def test_create_order():
    """Тест создания заказа."""
    customer_id = uuid4()
    order = Order(
        id=uuid4(),
        customer_id=customer_id
    )
    
    assert order.customer_id == customer_id
    assert order.status == OrderStatus.CREATED
    assert len(order.items) == 0
    assert order.total_amount.amount == 0


def test_add_item_to_order(sample_products):
    """Тест добавления товара в заказ."""
    order = Order(
        id=uuid4(),
        customer_id=uuid4()
    )
    
    product = sample_products[0]
    order.add_item(product, 2)
    
    assert len(order.items) == 1
    assert order.items[0].product_id == product.id
    assert order.items[0].quantity == 2
    assert order.total_amount.amount == product.price.amount * 2


def test_mark_order_as_paid():
    """Тест пометки заказа как оплаченного."""
    order = Order(
        id=uuid4(),
        customer_id=uuid4()
    )
    
    order.mark_as_paid()
    
    assert order.status == OrderStatus.PAID


def test_cannot_pay_cancelled_order():
    """Тест невозможности оплаты отмененного заказа."""
    order = Order(
        id=uuid4(),
        customer_id=uuid4(),
        status=OrderStatus.CANCELLED
    )
    
    with pytest.raises(ValueError, match="Невозможно оплатить заказ с текущим статусом"):
        order.mark_as_paid()


# Тесты для репозиториев

def test_product_repository():
    """Тест работы с репозиторием товаров."""
    repo = ProductRepository()
    
    # Создаем тестовый товар
    product = Product(
        id=uuid4(),
        name="Тестовый товар",
        description="Описание",
        price=Money(1000),
        category="Тест",
        stock_quantity=5
    )
    
    # Сохраняем и проверяем сохранение
    repo.save(product)
    assert repo.find_by_id(product.id) == product
    
    # Проверяем поиск по категории
    products_in_category = repo.find_by_category("Тест")
    assert len(products_in_category) == 1
    assert products_in_category[0] == product


def test_order_repository():
    """Тест работы с репозиторием заказов."""
    repo = OrderRepository()
    
    # Создаем тестовый заказ
    order = Order(
        id=uuid4(),
        customer_id=uuid4()
    )
    
    # Сохраняем и проверяем сохранение
    repo.save(order)
    assert repo.find_by_id(order.id) == order
    
    # Проверяем поиск по клиенту
    customer_orders = repo.find_by_customer(order.customer_id)
    assert len(customer_orders) == 1
    assert customer_orders[0] == order


# Тесты для сервиса платежей

def test_payment_service():
    """Тест работы сервиса платежей."""
    service = PaymentService()
    
    # Создаем тестовый заказ
    order = Order(
        id=uuid4(),
        customer_id=uuid4()
    )
    
    # Добавляем товар в заказ
    product = Product(
        id=uuid4(),
        name="Тестовый товар",
        description="Описание",
        price=Money(1000),
        category="Тест",
        stock_quantity=5
    )
    order.add_item(product, 2)
    
    # Создаем и обрабатываем платеж
    payment = service.create_payment(order)
    assert payment.status == PaymentStatus.PENDING
    
    processed_payment = service.process_payment(payment.id)
    assert processed_payment.status == PaymentStatus.COMPLETED
    assert processed_payment.processed_at is not None


# Интеграционный тест

def test_order_fulfillment_flow(sample_products, order_repository_with_products):
    """Тест полного цикла оформления заказа."""
    # Подготавливаем данные
    order_repo, product_repo = order_repository_with_products
    payment_service = PaymentService()
    
    # Создаем заказ
    customer_id = uuid4()
    order = Order(
        id=uuid4(),
        customer_id=customer_id
    )
    
    # Добавляем товары в заказ
    for product in sample_products:
        order.add_item(product, 1)
    
    # Сохраняем заказ
    order_repo.save(order)
    
    # Проверяем, что заказ создан корректно
    saved_order = order_repo.find_by_id(order.id)
    assert saved_order is not None
    assert len(saved_order.items) == 2
    
    # Создаем и обрабатываем платеж
    payment = payment_service.create_payment(order)
    assert payment.amount.amount == sum(p.price.amount for p in sample_products)
    
    processed_payment = payment_service.process_payment(payment.id)
    assert processed_payment.status == PaymentStatus.COMPLETED
    
    # Помечаем заказ как оплаченный
    order.mark_as_paid()
    order_repo.save(order)
    
    # Проверяем, что статус заказа изменился
    updated_order = order_repo.find_by_id(order.id)
    assert updated_order.status == OrderStatus.PAID
