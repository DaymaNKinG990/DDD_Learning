# DDD Learning - Курс по Domain-Driven Design

Этот проект представляет собой практический курс по изучению Domain-Driven Design (DDD) на основе книги Влада Хохонова "Изучаем DDD: предметно-ориентированное проектирование".

## 📚 О проекте

Курс структурирован по модулям и включает:
- Теоретические материалы по каждому аспекту DDD
- Практические примеры кода на Python
- Упражнения и тесты для закрепления знаний
- Полноценный пример системы бронирования отелей

## 🏗️ Структура курса

### Модули:
1. **Введение в DDD** - основы и ключевые концепции
2. **Единый язык** - Ubiquitous Language
3. **Ограниченные контексты** - Bounded Contexts
4. **Сущности** - Entities
5. **Объекты-значения** - Value Objects
6. **Агрегаты** - Aggregates
7. **Доменные события** - Domain Events
8. **Репозитории** - Repositories
9. **Сервисы приложения** - Application Services
10. **Архитектура** - Architecture patterns
11. **Интеграция и композиция** - Integration patterns

## 🚀 Быстрый старт

### Требования
- Python 3.12+
- uv (менеджер зависимостей)

### Установка
```bash
# Клонировать репозиторий
git clone <repository-url>
cd DDD_Learning

# Установить зависимости
uv sync

# Запустить тесты
uv run pytest

# Запустить документацию
uv run mkdocs serve
```

## 📖 Изучение

1. Начните с модуля `introduction_01`
2. Изучайте материалы по порядку
3. Выполняйте практические упражнения
4. Проверяйте знания с помощью тестов

## 🧪 Тестирование

```bash
# Запустить все тесты
uv run pytest

# Запустить тесты с покрытием
uv run pytest --cov=ddd_course

# Запустить конкретный модуль
uv run pytest ddd_course/entities_04/

# Запустить тесты bounded contexts
uv run pytest ddd_course/bounded_contexts_03/tests/
```

## 📚 Документация

Документация доступна через MkDocs:
```bash
uv run mkdocs serve
```

Откройте http://localhost:8000 в браузере.

## 🏗️ Архитектура проекта

Проект демонстрирует:
- Чистую архитектуру (Clean Architecture)
- Шестиугольную архитектуру (Hexagonal Architecture)
- CQRS (Command Query Responsibility Segregation)
- Event Sourcing
- Паттерны DDD

### Пример системы: Hotel Booking Platform

Полноценный пример системы бронирования отелей с тремя bounded contexts:
- **Booking Context** - управление бронированиями
- **Accounting Context** - финансовые операции
- **Accommodation Context** - размещение гостей

Документация по архитектуре:
- [Context Map](ddd_course/bounded_contexts_03/booking_platform_solution/CONTEXT_MAP.md)
- [Usage Examples](ddd_course/bounded_contexts_03/booking_platform_solution/USAGE_EXAMPLES.md)

## 🤝 Как контрибьютить

Мы приветствуем вклад в развитие курса! Вот как вы можете помочь:

### 🐛 Сообщить об ошибке

1. Проверьте, не была ли ошибка уже зарегистрирована в [Issues](https://github.com/DaymaNKinG990/DDD_Learning/issues)
2. Создайте новый issue с подробным описанием:
   - Что произошло
   - Что ожидалось
   - Шаги для воспроизведения
   - Версия Python и зависимостей

### 💡 Предложить улучшение

1. Создайте issue с описанием предлагаемого улучшения
2. Обсудите идею с сообществом
3. После одобрения создайте Pull Request

### 🔧 Создать Pull Request

1. **Форкните репозиторий**
2. **Создайте ветку для ваших изменений**:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Внесите изменения**:
   - Следуйте стилю кода проекта
   - Добавьте тесты для новых функций
   - Обновите документацию при необходимости
4. **Запустите тесты**:
   ```bash
   uv run pytest
   uv run ruff check .
   uv run mypy ddd_course/
   ```
5. **Создайте Pull Request** с описанием изменений

### 📝 Стандарты кода

- **Python**: Следуйте PEP 8 и используйте type hints
- **Документация**: Пишите docstring на английском языке
- **Тесты**: Покрытие тестами должно быть не менее 80%
- **Коммиты**: Используйте conventional commits
- **DDD**: Соблюдайте принципы Domain-Driven Design

### 🏷️ Conventional Commits

Используйте следующий формат для коммитов:
```
type(scope): description

[optional body]

[optional footer]
```

Примеры:
- `feat(aggregates): add order validation rules`
- `fix(tests): resolve import issues in bounded contexts`
- `docs(readme): add contributing guidelines`
- `refactor(domain): improve value object immutability`

### 🧪 Написание тестов

- **Unit тесты**: Для доменных объектов и сервисов
- **Integration тесты**: Для взаимодействия между bounded contexts
- **Fixtures**: Используйте pytest fixtures для переиспользуемых данных
- **Coverage**: Стремитесь к высокому покрытию кода

### 📚 Обновление документации

- Обновляйте README.md при добавлении новых функций
- Добавляйте примеры использования в соответствующие модули
- Обновляйте Context Map при изменении bounded contexts

## 📝 Лицензия

MIT License

## 📚 Источники

- Влад Хохонов "Изучаем DDD: предметно-ориентированное проектирование"
- Eric Evans "Domain-Driven Design: Tackling Complexity in the Heart of Software"
- Vaughn Vernon "Implementing Domain-Driven Design"
- Martin Fowler "Patterns of Enterprise Application Architecture"

## 🙏 Благодарности

Спасибо всем участникам сообщества за вклад в развитие курса и улучшение качества материалов по DDD.
