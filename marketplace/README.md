# Marketplace DDD Project

Полноценный проект маркетплейса в стиле Ozon, построенный с использованием принципов Domain-Driven Design (DDD) и SOLID.

## 🏗️ Архитектура

Проект следует принципам DDD с разделением на ограниченные контексты:

### Ограниченные контексты

- **Catalog** - Каталог товаров, категории, бренды
- **Orders** - Заказы, корзина, статусы заказов
- **Users** - Пользователи, аутентификация, профили
- **Payments** - Платежи, транзакции, интеграции с платежными системами
- **Shipping** - Доставка, адреса, трекинг
- **Reviews** - Отзывы, рейтинги
- **Notifications** - Уведомления, email, SMS

### Слои архитектуры

Каждый ограниченный контекст содержит:

- **Domain** - Доменные модели, сущности, объекты-значения
- **Application** - Сервисы приложения, команды, запросы
- **Infrastructure** - Репозитории, внешние сервисы, база данных
- **Interfaces** - API, контроллеры, представления

## 🎯 Принципы SOLID

- **S** - Single Responsibility: каждый класс отвечает за одну задачу
- **O** - Open/Closed: расширяемость без изменения существующего кода
- **L** - Liskov Substitution: замена типов без нарушения функциональности
- **I** - Interface Segregation: тонкие интерфейсы
- **D** - Dependency Inversion: зависимости от абстракций

## 🚀 Быстрый старт

### Предварительные требования

- Python 3.12+
- uv (менеджер пакетов)

### Установка

```bash
# Клонирование репозитория
git clone <repository-url>
cd marketplace

# Установка зависимостей
uv sync

# Запуск тестов
uv run pytest

# Запуск приложения
uv run uvicorn src.main:app --reload
```

### Структура проекта

```
marketplace/
├── src/
│   ├── catalog/           # Каталог товаров
│   │   ├── domain/        # Доменные модели
│   │   ├── application/   # Сервисы приложения
│   │   ├── infrastructure/ # Репозитории
│   │   └── interfaces/    # API контроллеры
│   ├── orders/            # Заказы
│   ├── users/             # Пользователи
│   ├── payments/          # Платежи
│   ├── shipping/          # Доставка
│   ├── reviews/           # Отзывы
│   ├── notifications/     # Уведомления
│   └── shared/            # Общие компоненты
├── tests/                 # Тесты
├── docs/                  # Документация
└── scripts/               # Скрипты
```

## 📚 Документация

- [Архитектура проекта](docs/ARCHITECTURE.md)
- [API документация](http://localhost:8000/docs) (после запуска)

## 🧪 Тестирование

### Запуск всех тестов

```bash
uv run pytest
```

### Запуск тестов с покрытием

```bash
uv run pytest --cov=src --cov-report=html
```

### Запуск конкретных тестов

```bash
# Тесты каталога
uv run pytest tests/test_catalog_domain.py -v

# Тесты заказов
uv run pytest tests/test_orders_domain.py -v
```

## 🔧 Разработка

### Добавление новых зависимостей

```bash
# Добавление зависимости
uv add package-name

# Добавление dev зависимости
uv add --dev package-name
```

### Форматирование кода

```bash
# Форматирование с black
uv run black src/ tests/

# Сортировка импортов
uv run isort src/ tests/
```

### Проверка типов

```bash
uv run mypy src/
```

## 📦 Основные компоненты

### Доменные модели

#### Каталог товаров

```python
from src.catalog.domain.entities import Product, Category, Brand
from src.catalog.domain.value_objects import Price, ProductName

# Создание товара
product = Product(
    id=ProductId(value="prod_123"),
    name=ProductName(value="iPhone 15"),
    price=Price(amount=Decimal("99999"), currency="RUB"),
    category_id=CategoryId(value="cat_electronics"),
    sku="IPHONE15-128GB"
)
```

#### Заказы

```python
from src.orders.domain.entities import Order, OrderItem

# Создание заказа
order = Order.create(
    customer_id="customer_123",
    shipping_address="123 Main St",
    billing_address="123 Main St"
)

# Добавление товара
item = OrderItem.create(
    product_id="prod_123",
    product_name="iPhone 15",
    quantity=1,
    unit_price=Decimal("99999")
)

order = order.add_item(item)
```

### Сервисы приложения

```python
from src.catalog.application.services import CatalogService

# Использование сервиса каталога
catalog_service = CatalogService(
    product_repository=product_repo,
    category_repository=category_repo,
    brand_repository=brand_repo
)

# Создание товара
product = await catalog_service.create_product(
    name="iPhone 15",
    description="Latest iPhone model",
    price=Price(amount=Decimal("99999"), currency="RUB"),
    category_id=CategoryId(value="cat_electronics"),
    sku="IPHONE15-128GB"
)
```

## 🌟 Особенности

### Неизменяемые модели

Все доменные модели используют `frozen=True` для обеспечения неизменяемости:

```python
class Product(Entity[ProductId]):
    model_config = ConfigDict(frozen=True)
    
    def update_price(self, new_price: Price) -> "Product":
        # Возвращает новый экземпляр вместо изменения существующего
        return Product(...)
```

### Валидация на уровне домена

```python
class Price(ValueObject):
    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v: Any) -> Decimal:
        if v < 0:
            raise ValueError("Price cannot be negative")
        return v
```

### Бизнес-правила в доменных моделях

```python
class Order(Entity[OrderId]):
    def cancel(self) -> "Order":
        if self.status in [OrderStatus.DELIVERED, OrderStatus.REFUNDED]:
            raise ValueError("Cannot cancel delivered or refunded order")
        return self.update_status(OrderStatus.CANCELLED)
```

## 🔄 Следующие шаги

1. **Инфраструктура** - реализация репозиториев с базой данных
2. **API** - создание REST API контроллеров
3. **Аутентификация** - интеграция с системой аутентификации
4. **Платежи** - интеграция с платежными системами
5. **Уведомления** - система уведомлений
6. **Микросервисы** - разделение на отдельные сервисы

## 📄 Лицензия

MIT License

## 🤝 Вклад в проект

1. Fork репозитория
2. Создайте feature branch (`git checkout -b feature/amazing-feature`)
3. Commit изменения (`git commit -m 'Add amazing feature'`)
4. Push в branch (`git push origin feature/amazing-feature`)
5. Откройте Pull Request