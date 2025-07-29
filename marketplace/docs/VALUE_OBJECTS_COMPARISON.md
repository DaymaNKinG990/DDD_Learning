# Сравнение подходов к Value Objects

В этом документе мы сравниваем три различных подхода к реализации Value Objects в Python: dataclass, Pydantic и гибридный подход.

## 1. Dataclass подход

### Код примера:
```python
@dataclass(frozen=True)
class DataclassPrice(DataclassValueObject):
    amount: float
    currency: str = "RUB"
    
    def _validate(self) -> None:
        if self.amount < 0:
            raise ValidationError("Price cannot be negative")
        if len(self.currency) != 3:
            raise ValidationError("Currency must be 3 letters")
```

### Преимущества:
- ✅ **Чистый Python** - нет внешних зависимостей
- ✅ **Полный контроль** - вы сами определяете всю логику валидации
- ✅ **Производительность** - dataclasses очень быстрые
- ✅ **Простота** - минимальный boilerplate код
- ✅ **Неизменяемость** - `frozen=True` обеспечивает иммутабельность

### Недостатки:
- ❌ **Ручная валидация** - нужно писать валидацию вручную
- ❌ **Нет встроенной сериализации** - нужно реализовывать `to_dict()` самостоятельно
- ❌ **Сложная типизация** - нужно вручную обрабатывать `Union`, `Generic` типы
- ❌ **Нет интеграции с экосистемой** - не работает "из коробки" с FastAPI, SQLAlchemy

### Когда использовать:
- Простые проекты без сложной валидации
- Когда важна производительность
- Когда не нужна интеграция с веб-фреймворками

## 2. Pydantic подход

### Код примера:
```python
class PydanticPrice(PydanticValueObject):
    amount: float = Field(gt=0, description="Price amount")
    currency: str = Field(default="RUB", min_length=3, max_length=3, description="Currency code")
    
    @field_validator("currency")
    @classmethod
    def validate_currency(cls, v: str) -> str:
        return v.upper()
```

### Преимущества:
- ✅ **Декларативная валидация** - валидация описывается в полях
- ✅ **Встроенная сериализация** - `model_dump()`, `model_validate()`
- ✅ **Автоматическая интеграция** - работает с FastAPI, SQLAlchemy
- ✅ **Богатая экосистема** - множество готовых валидаторов
- ✅ **Типизация** - строгая типизация с автодополнением в IDE
- ✅ **Документация** - автоматическая генерация схем

### Недостатки:
- ❌ **Внешняя зависимость** - нужно устанавливать Pydantic
- ❌ **Overhead** - дополнительный слой абстракции
- ❌ **Меньше контроля** - ограничен возможностями Pydantic
- ❌ **Сложность** - нужно изучать Pydantic API

### Когда использовать:
- Веб-приложения с API (FastAPI)
- Проекты с ORM (SQLAlchemy)
- Когда нужна автоматическая валидация и сериализация
- Большие проекты с множеством Value Objects

## 3. Гибридный подход

### Код примера:
```python
class HybridPrice(HybridValueObject):
    amount: float = Field(gt=0, description="Price amount")
    currency: str = Field(default="RUB", min_length=3, max_length=3, description="Currency code")
    
    @field_validator("currency")
    @classmethod
    def validate_currency(cls, v: str) -> str:
        return v.upper()
    
    def _validate_business_rules(self) -> None:
        if self.currency not in ["RUB", "USD", "EUR"]:
            raise ValidationError("Unsupported currency")
    
    def __add__(self, other: "HybridPrice") -> "HybridPrice":
        if self.currency != other.currency:
            raise ValidationError("Cannot add prices with different currencies")
```

### Преимущества:
- ✅ **Лучшее из двух миров** - Pydantic валидация + кастомная бизнес-логика
- ✅ **Гибкость** - можете добавлять любую бизнес-логику
- ✅ **Интеграция** - работает с экосистемой Pydantic
- ✅ **Расширяемость** - легко добавлять методы и операции
- ✅ **Читаемость** - четкое разделение валидации и бизнес-правил

### Недостатки:
- ❌ **Сложность** - больше кода для написания
- ❌ **Внешняя зависимость** - все еще нужен Pydantic
- ❌ **Дублирование** - валидация может дублироваться

### Когда использовать:
- Сложные доменные модели с бизнес-правилами
- Когда нужны операции между Value Objects
- Проекты, требующие гибкости и интеграции
- Enterprise-приложения

## Сравнительная таблица

| Критерий | Dataclass | Pydantic | Гибридный |
|----------|-----------|----------|-----------|
| **Производительность** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Простота** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Гибкость** | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Интеграция** | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Валидация** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Сериализация** | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Типизация** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Бизнес-логика** | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ |

## Рекомендации по выбору

### Для простых проектов:
```python
# Используйте dataclass подход
@dataclass(frozen=True)
class SimpleValueObject:
    value: str
    
    def __post_init__(self):
        if not self.value:
            raise ValueError("Value cannot be empty")
```

### Для веб-приложений:
```python
# Используйте Pydantic подход
class WebValueObject(BaseModel):
    value: str = Field(min_length=1, description="Required value")
    
    model_config = ConfigDict(frozen=True)
```

### Для сложных доменных моделей:
```python
# Используйте гибридный подход
class DomainValueObject(BaseModel):
    value: str = Field(min_length=1)
    
    model_config = ConfigDict(frozen=True)
    
    def __init__(self, **data):
        super().__init__(**data)
        self._validate_business_rules()
    
    def _validate_business_rules(self):
        # Сложная бизнес-логика
        pass
    
    def some_operation(self, other):
        # Операции между Value Objects
        pass
```

## Заключение

Выбор подхода зависит от требований проекта:

1. **Dataclass** - для простых, производительных решений
2. **Pydantic** - для веб-приложений с API
3. **Гибридный** - для сложных доменных моделей с бизнес-правилами

В нашем marketplace проекте мы используем **Pydantic подход**, так как:
- У нас есть API (FastAPI)
- Нужна автоматическая валидация и сериализация
- Проект достаточно большой для оправдания использования Pydantic
- Нужна интеграция с будущими ORM решениями