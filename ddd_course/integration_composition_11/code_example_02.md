# Пример Кода: Интеграция Контекстов через ACL и API

Этот пример иллюстрирует, как два Ограниченных Контекста ("Управление Заказами" и "Складской Учет") могут взаимодействовать с использованием Антикоррупционного Слоя (ACL) и вызовов API.

## Сценарий

*   **Контекст "Управление Заказами" (Ordering Context):** Отвечает за прием и обработку заказов клиентов. Перед подтверждением заказа ему необходимо проверить наличие товара на складе.
*   **Контекст "Складской Учет" (Inventory Context):** Отвечает за отслеживание количества товаров на складе. Он предоставляет API для проверки остатков.

## 1. API Контекста "Складской Учет" (Inventory Context)

Предположим, "Складской Учет" предоставляет следующий HTTP API endpoint для проверки наличия товара:

**Endpoint:** `GET /api/inventory/products/{productId}/stock`

**Пример ответа (JSON):**

```json
{
  "productId": "PROD123",
  "quantity": 15,
  "lastUpdated": "2023-10-26T10:30:00Z"
}
```

Или, если товара нет:

```json
{
  "productId": "PROD456",
  "quantity": 0,
  "lastUpdated": "2023-10-26T10:35:00Z"
}
```

## 2. Контекст "Управление Заказами" (Ordering Context)

### 2.1. Антикоррупционный Слой (ACL)

Внутри контекста "Управление Заказами" мы создадим ACL для изоляции нашей доменной модели от деталей API "Складского Учета".

#### 2.1.1. Интерфейс Сервиса Склада (Порт)

Определим интерфейс, который будет использоваться доменными и прикладными сервисами "Управления Заказами":

```python
# ordering_context/domain/inventory_service_interface.py
from abc import ABC, abstractmethod
from typing import Optional

class StockInfo:
    def __init__(self, product_id: str, quantity: int, is_available: bool):
        self.product_id = product_id
        self.quantity = quantity
        self.is_available = is_available

class InventoryServiceInterface(ABC):
    @abstractmethod
    def get_stock_info(self, product_id: str) -> Optional[StockInfo]:
        """
        Получает информацию о наличии товара на складе.
        Возвращает StockInfo или None, если товар не найден или произошла ошибка.
        """
        pass
```

#### 2.1.2. Адаптер Складского API (Реализация ACL)

Этот адаптер будет реализовывать `InventoryServiceInterface`, инкапсулируя логику вызова внешнего API и трансляции ответа.

```python
# ordering_context/infrastructure/inventory_acl_adapter.py
import requests # Для демонстрации HTTP-запроса
from typing import Optional

from ordering_context.domain.inventory_service_interface import InventoryServiceInterface, StockInfo

class InventoryApiAdapter(InventoryServiceInterface):
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')

    def get_stock_info(self, product_id: str) -> Optional[StockInfo]:
        try:
            response = requests.get(f"{self.base_url}/api/inventory/products/{product_id}/stock")
            response.raise_for_status()  # Вызовет исключение для HTTP-ошибок 4xx/5xx

            data = response.json()

            quantity = data.get("quantity", 0)
            is_available = quantity > 0

            return StockInfo(
                product_id=data.get("productId"),
                quantity=quantity,
                is_available=is_available
            )
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при запросе к API Склада для {product_id}: {e}")
            # Здесь может быть более сложная логика обработки ошибок,
            # например, возврат специального объекта ошибки или логирование
            return None
        except (KeyError, ValueError) as e:
            print(f"Ошибка парсинга ответа от API Склада для {product_id}: {e}")
            return None

```
**Примечание:** В реальном приложении использовался бы более надежный HTTP-клиент и лучшая обработка ошибок, возможно, с использованием паттерна Circuit Breaker.

### 2.2. Прикладной Сервис (Application Service)

Прикладной сервис в "Управлении Заказами" использует `InventoryServiceInterface` для проверки наличия товара.

```python
# ordering_context/application/order_service.py
from ordering_context.domain.inventory_service_interface import InventoryServiceInterface
# Предположим, есть класс Order и репозиторий
# from ordering_context.domain.order import Order, OrderItem
# from ordering_context.domain.order_repository_interface import OrderRepositoryInterface

class OrderPlacementService:
    def __init__(self, inventory_service: InventoryServiceInterface): #, order_repository: OrderRepositoryInterface):
        self._inventory_service = inventory_service
        # self._order_repository = order_repository

    def place_order(self, customer_id: str, product_id: str, quantity_ordered: int) -> str:
        stock_info = self._inventory_service.get_stock_info(product_id)

        if not stock_info:
            raise ValueError(f"Не удалось получить информацию о товаре {product_id} со склада.")

        if not stock_info.is_available or stock_info.quantity < quantity_ordered:
            raise ValueError(f"Товар {product_id} отсутствует на складе в достаточном количестве.")

        # Логика создания заказа...
        # order = Order.create(customer_id, [OrderItem(product_id, quantity_ordered, price_per_item)])
        # self._order_repository.save(order)

        print(f"Заказ на товар {product_id} (кол-во: {quantity_ordered}) успешно размещен.")
        return f"Order_XYZ123" # Возвращаем ID созданного заказа

```

## 3. Конфигурация и Использование

```python
# main.py (или точка входа вашего приложения)

from ordering_context.infrastructure.inventory_acl_adapter import InventoryApiAdapter
from ordering_context.application.order_service import OrderPlacementService

# URL API Складского Учета (может быть взят из конфигурации)
INVENTORY_API_URL = "http://localhost:8081" # Пример

if __name__ == "__main__":
    # Инициализация адаптера ACL
    inventory_adapter = InventoryApiAdapter(base_url=INVENTORY_API_URL)

    # Инициализация прикладного сервиса с внедренным адаптером
    order_service = OrderPlacementService(inventory_service=inventory_adapter)

    try:
        # Пример использования: размещение заказа
        # В реальном приложении эти данные пришли бы из UI или другого источника
        customer_id = "CUST001"
        product_id_to_order = "PROD123"
        quantity = 2

        print(f"Попытка разместить заказ для клиента {customer_id} на товар {product_id_to_order} (кол-во: {quantity})...")
        order_id = order_service.place_order(customer_id, product_id_to_order, quantity)
        print(f"Заказ успешно размещен. ID заказа: {order_id}")

    except ValueError as e:
        print(f"Ошибка при размещении заказа: {e}")
    except Exception as e:
        print(f"Непредвиденная ошибка: {e}")

    # Пример с товаром, которого нет в наличии (или его мало)
    # Для этого нужно, чтобы API Склада вернул quantity: 0 для "PROD456"
    # или quantity < 5 для "PROD789"
    try:
        product_id_unavailable = "PROD456" # Предположим, этого товара нет
        quantity_unavailable = 1
        print(f"\nПопытка разместить заказ на отсутствующий товар {product_id_unavailable}...")
        order_service.place_order(customer_id, product_id_unavailable, quantity_unavailable)
    except ValueError as e:
        print(f"Ошибка при размещении заказа: {e}")

```

## Обсуждение

*   **Изоляция:** ACL (`InventoryApiAdapter`) изолирует доменную логику "Управления Заказами" от деталей реализации и модели данных "Складского Учета". Если API склада изменится, изменения в основном коснутся только адаптера.
*   **Тестируемость:** `OrderPlacementService` можно легко тестировать, подменяя `InventoryServiceInterface` на мок-объект, что позволяет тестировать логику размещения заказа независимо от внешнего API.
*   **Ясность:** Домен "Управления Заказами" оперирует понятным ему интерфейсом `InventoryServiceInterface` и объектом `StockInfo`, а не деталями HTTP-запросов и JSON-ответов.
*   **Трансляция:** Адаптер выполняет трансляцию данных из формата API "Складского Учета" в формат, используемый в "Управлении Заказами" (`StockInfo`).

Этот пример демонстрирует один из способов интеграции контекстов, который способствует поддержанию слабой связанности и чистоты доменных моделей.
