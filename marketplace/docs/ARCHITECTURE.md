# Архитектура Marketplace DDD проекта

## Обзор

Проект построен с использованием принципов Domain-Driven Design (DDD) и следует архитектурным паттернам Clean Architecture. Основная цель - создание масштабируемого и поддерживаемого маркетплейса в стиле Ozon.

## Архитектурные принципы

### 1. Domain-Driven Design (DDD)

Проект следует принципам DDD:

- **Ограниченные контексты (Bounded Contexts)** - четкое разделение доменов
- **Универсальный язык (Ubiquitous Language)** - единая терминология
- **Стратегическое проектирование** - карта контекстов и их отношений
- **Тактическое проектирование** - сущности, объекты-значения, агрегаты

### 2. Clean Architecture

Архитектура разделена на слои:

```
┌─────────────────────────────────────┐
│           Interfaces                │ ← API, Controllers
├─────────────────────────────────────┤
│        Application                  │ ← Use Cases, Services
├─────────────────────────────────────┤
│           Domain                    │ ← Entities, Value Objects
├─────────────────────────────────────┤
│        Infrastructure              │ ← Repositories, External Services
└─────────────────────────────────────┘
```

### 3. SOLID принципы

- **S** - Single Responsibility: каждый класс отвечает за одну задачу
- **O** - Open/Closed: расширяемость без изменения существующего кода
- **L** - Liskov Substitution: замена типов без нарушения функциональности
- **I** - Interface Segregation: тонкие интерфейсы
- **D** - Dependency Inversion: зависимости от абстракций

## Ограниченные контексты

### 1. Catalog (Каталог)

**Ответственность**: Управление товарами, категориями, брендами

**Основные сущности**:
- `Product` - товар
- `Category` - категория
- `Brand` - бренд

**Объекты-значения**:
- `ProductId`, `CategoryId`, `BrandId` - идентификаторы
- `Price` - цена с валидацией
- `ProductName`, `ProductDescription` - названия и описания

**Бизнес-правила**:
- Цена не может быть отрицательной
- Название товара не может быть пустым
- SKU должен быть уникальным

### 2. Orders (Заказы)

**Ответственность**: Управление заказами, корзиной, статусами

**Основные сущности**:
- `Order` - заказ
- `OrderItem` - позиция заказа

**Объекты-значения**:
- `OrderId`, `OrderItemId` - идентификаторы
- `OrderStatus` - статус заказа (enum)
- `OrderTotal` - расчет итоговой суммы

**Бизнес-правила**:
- Заказ может быть отменен только до доставки
- Статус заказа изменяется по определенным правилам
- Автоматический пересчет суммы при изменении позиций

## Доменные модели

### Сущности (Entities)

Все сущности наследуются от базового класса `Entity`:

```python
class Product(Entity[ProductId]):
    name: ProductName
    description: ProductDescription
    price: Price
    category_id: CategoryId
    brand_id: Optional[BrandId]
    sku: str
    is_active: bool
    # ...
```

**Характеристики**:
- Имеют уникальный идентификатор
- Могут изменять состояние
- Содержат бизнес-логику
- Неизменяемы (frozen=True)

### Объекты-значения (Value Objects)

Все объекты-значения наследуются от базового класса `ValueObject`:

```python
class Price(ValueObject):
    amount: Decimal
    currency: str
    
    def __add__(self, other: "Price") -> "Price":
        # Бизнес-логика сложения цен
```

**Характеристики**:
- Неизменяемы
- Не имеют идентификатора
- Содержат валидацию
- Могут содержать бизнес-логику

## Слои архитектуры

### Domain Layer

Содержит доменные модели и бизнес-логику:

- **Entities** - сущности с идентификаторами
- **Value Objects** - объекты-значения
- **Repositories** - интерфейсы репозиториев
- **Domain Services** - доменные сервисы
- **Domain Events** - доменные события

### Application Layer

Содержит сценарии использования:

- **Application Services** - координация доменных объектов
- **Commands/Queries** - команды и запросы
- **DTOs** - объекты передачи данных
- **Use Cases** - сценарии использования

### Infrastructure Layer

Содержит техническую реализацию:

- **Repositories** - реализация репозиториев
- **External Services** - интеграция с внешними сервисами
- **Database** - работа с базой данных
- **Caching** - кэширование

### Interfaces Layer

Содержит точки входа в систему:

- **API Controllers** - REST API
- **Event Handlers** - обработчики событий
- **CLI Commands** - командная строка

## Паттерны проектирования

### 1. Repository Pattern

```python
class ProductRepository(ABC):
    @abstractmethod
    async def save(self, product: Product) -> Product:
        pass
    
    @abstractmethod
    async def get_by_id(self, product_id: ProductId) -> Optional[Product]:
        pass
```

### 2. Factory Pattern

```python
class OrderItem:
    @classmethod
    def create(cls, product_id: str, quantity: int, unit_price: Decimal) -> "OrderItem":
        # Создание с валидацией
```

### 3. Specification Pattern

Для сложных запросов к репозиториям.

### 4. Event Sourcing

Для отслеживания изменений состояния.

## Тестирование

### Стратегия тестирования

1. **Unit Tests** - тестирование доменных моделей
2. **Integration Tests** - тестирование репозиториев
3. **Application Tests** - тестирование сервисов приложения
4. **End-to-End Tests** - тестирование API

### Пример теста

```python
def test_create_product(self):
    product = Product(
        id=ProductId(value="prod_123"),
        name=ProductName(value="Test Product"),
        price=Price(amount=Decimal("100"), currency="RUB"),
        # ...
    )
    assert product.name.value == "Test Product"
```

## Масштабирование

### Горизонтальное масштабирование

- Микросервисная архитектура
- API Gateway
- Load Balancing
- Caching (Redis)

### Вертикальное масштабирование

- Оптимизация запросов
- Индексы базы данных
- Асинхронная обработка

## Мониторинг и логирование

- Структурированное логирование
- Метрики производительности
- Трейсинг запросов
- Алерты

## Безопасность

- Аутентификация и авторизация
- Валидация входных данных
- Защита от SQL-инъекций
- Rate limiting