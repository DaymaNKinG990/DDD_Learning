"""
Пример реализации ограниченных контекстов в системе электронной коммерции.

Этот модуль демонстрирует, как различные ограниченные контексты взаимодействуют
в рамках одной системы, сохраняя при этом свою изолированность.
"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Dict, Optional
from uuid import UUID, uuid4

# ============================================
# Общие типы данных (Shared Kernel)
# ============================================

@dataclass(frozen=True)
class Money:
    """Денежная сумма с валютой."""
    amount: float
    currency: str = "RUB"


class OrderStatus(str, Enum):
    """Статусы заказа."""
    CREATED = "Создан"
    PAID = "Оплачен"
    SHIPPED = "Отправлен"
    DELIVERED = "Доставлен"
    CANCELLED = "Отменен"


# ============================================
# Контекст: Каталог товаров (Product Catalog)
# ============================================

@dataclass
class Product:
    """Товар в каталоге."""
    id: UUID
    name: str
    description: str
    price: Money
    category: str
    stock_quantity: int
    is_active: bool = True


class ProductRepository:
    """Репозиторий для работы с товарами."""
    def __init__(self):
        self._products: Dict[UUID, Product] = {}
    
    def find_by_id(self, product_id: UUID) -> Optional[Product]:
        return self._products.get(product_id)
    
    def save(self, product: Product) -> None:
        self._products[product.id] = product
    
    def find_by_category(self, category: str) -> List[Product]:
        return [p for p in self._products.values() 
                if p.category == category and p.is_active]


# ============================================
# Контекст: Заказы (Orders)
# ============================================

@dataclass
class OrderItem:
    """Позиция в заказе."""
    product_id: UUID
    product_name: str
    quantity: int
    unit_price: Money
    
    @property
    def total_price(self) -> Money:
        return Money(amount=self.unit_price.amount * self.quantity)


@dataclass
class Order:
    """Заказ в системе."""
    id: UUID
    customer_id: UUID
    items: List[OrderItem] = field(default_factory=list)
    status: OrderStatus = OrderStatus.CREATED
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    @property
    def total_amount(self) -> Money:
        if not self.items:
            return Money(amount=0)
        total = sum(item.total_price.amount for item in self.items)
        return Money(amount=total)
    
    def add_item(self, product: Product, quantity: int) -> None:
        """Добавить товар в заказ."""
        if quantity <= 0:
            raise ValueError("Количество должно быть положительным числом")
        
        # Проверяем, есть ли уже такой товар в заказе
        for item in self.items:
            if item.product_id == product.id:
                item.quantity += quantity
                self.updated_at = datetime.now()
                return
        
        # Если товара еще нет в заказе, добавляем новую позицию
        self.items.append(
            OrderItem(
                product_id=product.id,
                product_name=product.name,
                quantity=quantity,
                unit_price=product.price
            )
        )
        self.updated_at = datetime.now()
    
    def mark_as_paid(self) -> None:
        """Пометить заказ как оплаченный."""
        if self.status != OrderStatus.CREATED:
            raise ValueError("Невозможно оплатить заказ с текущим статусом")
        self.status = OrderStatus.PAID
        self.updated_at = datetime.now()


class OrderRepository:
    """Репозиторий для работы с заказами."""
    def __init__(self):
        self._orders: Dict[UUID, Order] = {}
    
    def find_by_id(self, order_id: UUID) -> Optional[Order]:
        return self._orders.get(order_id)
    
    def save(self, order: Order) -> None:
        self._orders[order.id] = order
    
    def find_by_customer(self, customer_id: UUID) -> List[Order]:
        return [o for o in self._orders.values() 
                if o.customer_id == customer_id]


# ============================================
# Контекст: Оплата (Payments)
# ============================================

class PaymentStatus(str, Enum):
    """Статусы платежа."""
    PENDING = "В обработке"
    COMPLETED = "Завершен"
    FAILED = "Неудачный"
    REFUNDED = "Возвращен"


@dataclass
class Payment:
    """Платеж в системе."""
    id: UUID
    order_id: UUID
    amount: Money
    status: PaymentStatus = PaymentStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    processed_at: Optional[datetime] = None
    
    def mark_as_completed(self) -> None:
        """Пометить платеж как завершенный."""
        self.status = PaymentStatus.COMPLETED
        self.processed_at = datetime.now()
    
    def mark_as_failed(self) -> None:
        """Пометить платеж как неудачный."""
        self.status = PaymentStatus.FAILED
        self.processed_at = datetime.now()


class PaymentService:
    """Сервис для работы с платежами."""
    def __init__(self):
        self._payments: Dict[UUID, Payment] = {}
    
    def create_payment(self, order: Order) -> Payment:
        """Создать платеж для заказа."""
        payment = Payment(
            id=uuid4(),
            order_id=order.id,
            amount=order.total_amount
        )
        self._payments[payment.id] = payment
        return payment
    
    def process_payment(self, payment_id: UUID) -> Payment:
        """Обработать платеж (имитация)."""
        payment = self._payments.get(payment_id)
        if not payment:
            raise ValueError("Платеж не найден")
        
        # В реальной системе здесь был бы вызов платежного шлюза
        # Для примера просто помечаем платеж как завершенный
        payment.mark_as_completed()
        return payment


# ============================================
# Интеграция контекстов
# ============================================

def demonstrate_bounded_contexts():
    """Демонстрация взаимодействия ограниченных контекстов."""
    # Инициализируем репозитории и сервисы
    product_repo = ProductRepository()
    order_repo = OrderRepository()
    payment_service = PaymentService()
    
    # Создаем тестовые товары
    laptop = Product(
        id=uuid4(),
        name="Ноутбук",
        description="Мощный игровой ноутбук",
        price=Money(150000),
        category="Электроника",
        stock_quantity=10
    )
    
    phone = Product(
        id=uuid4(),
        name="Смартфон",
        description="Флагманский смартфон",
        price=Money(120000),
        category="Электроника",
        stock_quantity=20
    )
    
    # Сохраняем товары в репозиторий
    product_repo.save(laptop)
    product_repo.save(phone)
    
    # Создаем заказ
    customer_id = uuid4()
    order = Order(
        id=uuid4(),
        customer_id=customer_id
    )
    
    # Добавляем товары в заказ
    order.add_item(laptop, 1)
    order.add_item(phone, 2)
    
    # Сохраняем заказ
    order_repo.save(order)
    
    print(f"Создан заказ №{order.id}")
    print(f"Общая сумма: {order.total_amount.amount} {order.total_amount.currency}")
    
    # Создаем и обрабатываем платеж
    payment = payment_service.create_payment(order)
    print(f"Создан платеж {payment.id} на сумму {payment.amount.amount} {payment.amount.currency}")
    
    # Обрабатываем платеж
    processed_payment = payment_service.process_payment(payment.id)
    print(f"Статус платежа: {processed_payment.status}")
    
    # Если платеж успешен, обновляем статус заказа
    if processed_payment.status == PaymentStatus.COMPLETED:
        order.mark_as_paid()
        order_repo.save(order)
        print(f"Статус заказа: {order.status}")
    
    # Выводим информацию о заказе
    print("\nДетали заказа:")
    print(f"Клиент: {order.customer_id}")
    print(f"Дата создания: {order.created_at}")
    print("Товары:")
    for item in order.items:
        print(f"- {item.product_name}: {item.quantity} x {item.unit_price.amount} {item.unit_price.currency}")
    print(f"Итого: {order.total_amount.amount} {order.total_amount.currency}")


if __name__ == "__main__":
    demonstrate_bounded_contexts()
