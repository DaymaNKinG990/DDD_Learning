# Marketplace Microservices Architecture

## Обзор

Проект реализован в виде микросервисной архитектуры, где каждый домен является отдельным сервисом с собственным API.

## Архитектура

### Сервисы

1. **API Gateway** (порт 8000) - Единая точка входа для всех запросов
2. **Catalog Service** (порт 8001) - Управление каталогом товаров
3. **Orders Service** (порт 8002) - Управление заказами
4. **Users Service** (порт 8003) - Управление пользователями
5. **Auth Service** (порт 8004) - Аутентификация и авторизация
6. **Reviews Service** (порт 8005) - Управление отзывами
7. **Notifications Service** (порт 8006) - Уведомления

### Инфраструктура

- **PostgreSQL** (порт 5432) - Общая база данных
- **Redis** (порт 6379) - Кэширование и сессии
- **Nginx** (порт 80/443) - Обратный прокси
- **pgAdmin** (порт 5050) - Управление БД
- **Redis Commander** (порт 8081) - Управление Redis

## Запуск

### Все сервисы сразу

```bash
docker-compose -f docker-compose.microservices.yml up -d
```

### Отдельные сервисы

```bash
# Только инфраструктура
docker-compose -f docker-compose.microservices.yml up -d postgres redis

# Конкретный сервис
docker-compose -f docker-compose.microservices.yml up -d catalog
```

## API Endpoints

### API Gateway (основной доступ)

- `http://localhost:8000/` - Главная страница
- `http://localhost:8000/docs` - Swagger документация
- `http://localhost:8000/health` - Проверка здоровья всех сервисов

### Прямой доступ к сервисам

- **Catalog**: `http://localhost:8001/`
- **Orders**: `http://localhost:8002/`
- **Users**: `http://localhost:8003/`
- **Auth**: `http://localhost:8004/`
- **Reviews**: `http://localhost:8005/`
- **Notifications**: `http://localhost:8006/`

## Межсервисное общение

### Через API Gateway

```bash
# Получить товары через Gateway
curl http://localhost:8000/catalog/products

# Создать заказ через Gateway
curl -X POST http://localhost:8000/orders \
  -H "Content-Type: application/json" \
  -d '{"user_id": "123", "items": [...]}'
```

### Прямое обращение к сервисам

```bash
# Прямое обращение к Catalog Service
curl http://localhost:8001/catalog/products

# Прямое обращение к Orders Service
curl http://localhost:8002/orders
```

## Разработка

### Структура проекта

```
marketplace/
├── services/
│   ├── gateway/
│   │   ├── main.py
│   │   └── Dockerfile
│   ├── catalog/
│   │   ├── main.py
│   │   └── Dockerfile
│   ├── orders/
│   │   ├── main.py
│   │   └── Dockerfile
│   └── ...
├── src/
│   ├── catalog/
│   ├── orders/
│   ├── users/
│   ├── auth/
│   ├── reviews/
│   ├── notifications/
│   └── shared/
├── docker-compose.microservices.yml
└── README_MICROSERVICES.md
```

### Добавление нового сервиса

1. Создать папку в `services/`
2. Создать `main.py` с FastAPI приложением
3. Создать `Dockerfile`
4. Добавить сервис в `docker-compose.microservices.yml`
5. Обновить `ServiceRegistry` в `service_client.py`

### Пример нового сервиса

```python
# services/payments/main.py
from fastapi import FastAPI
from src.shared.infrastructure.middleware import LoggingMiddleware

app = FastAPI(title="Payments Service")
app.add_middleware(LoggingMiddleware)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "payments"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8007)
```

## Мониторинг

### Логи

```bash
# Логи конкретного сервиса
docker logs marketplace_catalog

# Логи всех сервисов
docker-compose -f docker-compose.microservices.yml logs -f
```

### Health Checks

```bash
# Проверка здоровья через Gateway
curl http://localhost:8000/health

# Прямая проверка сервиса
curl http://localhost:8001/health
```

### Метрики

- **pgAdmin**: `http://localhost:5050` (admin@marketplace.com / admin_password)
- **Redis Commander**: `http://localhost:8081`

## Масштабирование

### Горизонтальное масштабирование

```bash
# Масштабировать Catalog Service
docker-compose -f docker-compose.microservices.yml up -d --scale catalog=3
```

### Вертикальное масштабирование

Изменить ресурсы в `docker-compose.microservices.yml`:

```yaml
catalog:
  deploy:
    resources:
      limits:
        cpus: '2'
        memory: 2G
      reservations:
        cpus: '1'
        memory: 1G
```

## Безопасность

### Аутентификация

Все сервисы используют JWT токены для аутентификации. Токены проверяются в каждом сервисе.

### Сетевая безопасность

- Все сервисы работают в изолированной сети `marketplace_network`
- Внешний доступ только через API Gateway
- Nginx обеспечивает дополнительный уровень безопасности

## Производительность

### Кэширование

- Redis используется для кэширования данных
- Каждый сервис может кэшировать свои данные
- API Gateway кэширует ответы от сервисов

### Балансировка нагрузки

Nginx может балансировать нагрузку между несколькими экземплярами сервисов.

## Отладка

### Локальная разработка

```bash
# Запустить только инфраструктуру
docker-compose -f docker-compose.microservices.yml up -d postgres redis

# Запустить сервис локально
cd services/catalog
uv run uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

### Отладка в Docker

```bash
# Войти в контейнер
docker exec -it marketplace_catalog bash

# Просмотреть логи
docker logs -f marketplace_catalog
```

## Развертывание

### Production

1. Изменить переменные окружения
2. Настроить SSL сертификаты
3. Настроить мониторинг
4. Настроить бэкапы

### CI/CD

```yaml
# .github/workflows/deploy.yml
name: Deploy Microservices
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Build and deploy
        run: |
          docker-compose -f docker-compose.microservices.yml build
          docker-compose -f docker-compose.microservices.yml up -d
``` 