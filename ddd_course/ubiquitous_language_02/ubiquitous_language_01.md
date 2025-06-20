# Ubiquitous Language (Единый язык)

## Что такое Ubiquitous Language?

**Ubiquitous Language** (Единый язык) — это общий язык, который используется всеми участниками проекта (разработчиками, бизнес-аналитиками, заказчиками) для обсуждения предметной области. Этот язык должен быть:

- **Единым** — один термин должен означать одно и то же для всех
- **Точным** — термины должны точно отражать бизнес-концепции
- **Используемым в коде** — имена классов, методов и переменных должны соответствовать терминам единого языка

### Связь с Ограниченным Контекстом (Bounded Context)

Важно понимать, что Единый язык не является универсальным для всего бизнес-домена. Он **разрабатывается и применяется в границах конкретного Ограниченного Контекста**. В одном контексте (например, "Продажи") термин "Клиент" может означать одно, а в другом (например, "Техподдержка") — совсем другое, с иным набором атрибутов и поведения. Именно Ограниченный Контекст дает языку точность и однозначность.

---

## Зачем нужен Ubiquitous Language?

1. **Устраняет недопонимание** между техниками и бизнес-экспертами
2. **Уменьшает потери** при переводе требований в код
3. **Делает код самодокументированным** — имена в коде напрямую отражают бизнес-термины
4. **Ускоряет разработку** за счёт чёткого понимания требований

## Как разработать Ubiquitous Language?

### 1. Выявление терминов

- Проводите воркшопы с участием всех заинтересованных сторон
- Фиксируйте все бизнес-термины и их определения
- Обращайте внимание на синонимы и омонимы

### 2. Уточнение определений

- Задавайте уточняющие вопросы: "Что именно означает этот термин?"
- Ищите пограничные случаи: "А что если...?"
- Фиксируйте примеры использования терминов

### 3. Отражение в коде

```python
# Плохо
def process(data):
    # Что такое data? Что делает этот метод?
    pass

# Хорошо
def calculate_order_total(order: Order) -> Money:
    """Рассчитывает общую сумму заказа с учётом скидок.

    Аргументы:
        order: Заказ, для которого рассчитывается сумма

    Возвращает:
        Общая сумма заказа в виде объекта Money
    """
    # ...
```

### 4. Поддержание актуальности

- Регулярно пересматривайте и уточняйте термины
- Включайте обсуждение терминов в процесс код-ревью
- Документируйте решения об изменениях в языке

## Практические советы

1. **Избегайте технического жаргона** при обсуждении с бизнес-экспертами
2. **Создайте глоссарий** с определениями терминов
3. **Используйте термины последовательно** во всех артефактах (документация, код, тесты)
4. **Не бойтесь уточнять** — лучше задать лишний вопрос, чем сделать неправильное предположение

## Пример из практики

Рассмотрим пример системы бронирования отелей:

| Термин | Определение |
|--------|------------|
| Бронь | Договорённость о предоставлении номера гостю на определённые даты |
| Номер | Отдельное помещение в отеле, доступное для бронирования |
| Тариф | Набор условий и цена за проживание в номере |
| Гость | Человек, который бронирует или занимает номер |
| Заезд | Процесс регистрации гостя в отеле |
| Выезд | Процесс освобождения номера гостем |

## Распространённые ошибки

1. **Технические термины в общении с бизнесом**
   - ❌ "Нам нужно добавить новую сущность в репозиторий"
   - ✅ "Нам нужно завести новую карточку для учета дополнительных услуг"

2. **Использование разных терминов для одного понятия**
   - ❌ В коде: `user`, в документации: `client`, в интерфейсе: `customer`
   - ✅ Во всех местах: `клиент`

3. **Игнорирование нюансов терминологии**
   - ❌ "Заказ" и "Покупка" — это одно и то же
   - ✅ "Заказ" — намерение купить, "Покупка" — завершённая сделка

## Заключение

Разработка и поддержание Ubiquitous Language — это непрерывный процесс, который требует активного участия всех членов команды. Инвестиции в создание общего языка окупаются за счёт снижения количества ошибок, ускорения разработки и создания более качественного программного обеспечения.
