# Решение: Система управления отелем с ограниченными контекстами

Это решение практического задания по реализации ограниченных контекстов для системы управления отелем.

## Структура решения

```
booking_platform_solution/
├── README.md                    # Этот файл
├── pyproject.toml               # Зависимости проекта
├── src/
│   ├── shared_kernel/          # Общие типы и утилиты
│   │   └── __init__.py
│   │   └── domain.py
│   │
│   ├── booking/                # Контекст бронирования
│   │   ├── __init__.py
│   │   ├── domain.py
│   │   ├── application.py
│   │   ├── infrastructure.py
│   │   └── interfaces.py
│   │
│   ├── accommodation/          # Контекст проживания
│   │   ├── __init__.py
│   │   ├── domain.py
│   │   ├── application.py
│   │   └── infrastructure.py
│   │
│   ├── accounting/             # Контекст бухгалтерии
│   │   ├── __init__.py
│   │   ├── domain.py
│   │   ├── application.py
│   │   └── infrastructure.py
│   │
│   └── housekeeping/           # Дополнительный контекст уборки
│       ├── __init__.py
│       ├── domain.py
│       └── application.py
│
└── tests/                     # Тесты
    ├── __init__.py
    ├── test_booking_context.py
    ├── test_accommodation_context.py
    ├── test_accounting_context.py
    └── test_housekeeping_context.py
```

## Как запустить

1. Установите зависимости:
   ```bash
   pip install -e .
   ```

2. Запустите тесты:
   ```bash
   pytest tests/
   ```

## Основные компоненты

### 1. Общее ядро (Shared Kernel)
- Типы данных: Money, DateRange, Address
- Утилиты для работы с датами и валютами

### 2. Контекст бронирования (Booking)
- Управление бронированием номеров
- Проверка доступности номеров
- Отмена и изменение бронирований

### 3. Контекст проживания (Accommodation)
- Заселение и выселение гостей
- Управление состоянием номеров
- Отслеживание текущих постояльцев

### 4. Контекст бухгалтерии (Accounting)

#### Основные сущности:
- **Счет (Invoice)** - документ на оплату проживания и дополнительных услуг
- **Платеж (Payment)** - информация о произведенной оплате
- **Финансовый период (FinancialPeriod)** - отчетный период для финансовой отчетности
- **Возврат (Refund)** - информация о возврате средств

#### Основной функционал:
- Создание и управление счетами
- Обработка платежей через платежные шлюзы
- Управление финансовыми периодами
- Генерация финансовых отчетов
- Обработка возвратов и корректировок
- Интеграция с системой бронирования

#### Интеграционные точки:
1. Создание счета при подтверждении бронирования
2. Обновление статуса бронирования при оплате счета
3. Создание возврата при отмене бронирования
4. Корректировка счета при досрочном выезде

#### Пример использования:
```python
# Создание счета
invoice = await accounting_service.create_invoice(
    guest_id=guest.id,
    booking_id=booking.id,
    items=[
        InvoiceItemDTO(
            description="Номер на двоих (3 ночи)",
            quantity=Decimal("3"),
            unit_price=Money(amount=Decimal("2500.00")),
            tax_rate=Decimal("20"),
            discount=Money(amount=Decimal("0.00"))
        )
    ],
    due_date=date.today() + timedelta(days=7)
)

# Оплата счета
payment = await accounting_service.record_payment(
    invoice_id=invoice.id,
    amount=invoice.total,
    payment_method=PaymentMethod.CREDIT_CARD.value,
    process_online=True
)

# Генерация отчета
report = await accounting_service.generate_daily_report(date.today())
```

### 5. Контекст уборки (Housekeeping) - дополнительный
- Планирование уборки номеров
- Отслеживание статуса уборки
- Управление горничными

## Взаимодействие контекстов

### 1. Событийная архитектура
- **Событие BookingConfirmed** → Создание счета
- **Событие PaymentReceived** → Подтверждение бронирования
- **Событие BookingCancelled** → Создание возврата
- **Событие EarlyCheckout** → Корректировка счета

### 2. Антикоррупционный слой
- Преобразование сущностей между контекстами
- Валидация и нормализация данных
- Обработка версионности API

### 3. Саги для распределенных транзакций
1. **Оплата бронирования**
   - Бронирование → Счет → Платеж → Подтверждение
   - Компенсирующие действия при ошибках

2. **Отмена бронирования**
   - Отмена бронирования → Возврат средств → Освобождение номера

3. **Досрочный выезд**
   - Регистрация выезда → Корректировка счета → Возврат средств

## Пример использования

### Создание и оплата бронирования

```python
# 1. Создаем бронирование
booking = await booking_service.create_booking(
    room_id=room.id,
    guest_id=guest.id,
    check_in=date(2025, 7, 1),
    check_out=date(2025, 7, 10),
    guest_count=2,
    special_requests="Детская кроватка"
)

# 2. Получаем счет на оплату
invoices = await accounting_service.uow.invoices.list_by_booking(booking.id)
invoice = invoices[0]

# 3. Оплачиваем счет
payment = await accounting_service.record_payment(
    invoice_id=invoice.id,
    amount=invoice.total,
    payment_method=PaymentMethod.CREDIT_CARD.value,
    process_online=True
)

# 4. Производим заселение (статус брони автоматически обновляется на PAID)
check_in = await accommodation_service.check_in(
    booking_id=booking.id,
    room_id=booking.room_id,
    guest_id=booking.guest_id
)

# 5. При досрочном выезде создается корректировка
await accommodation_service.check_out_guest(
    booking_id=booking.id,
    actual_check_out=date(2025, 7, 8)  # На 2 дня раньше
)

# 6. Получаем обновленный счет с корректировкой
updated_invoice = await accounting_service.uow.invoices.get_by_id(invoice.id)
print(f"Итоговая сумма: {updated_invoice.total.amount} руб.")
```

### Генерация отчетов

```python
# Ежедневный отчет
report = await accounting_service.generate_daily_report(date.today())

# Отчет за период
start_date = date(2025, 7, 1)
end_date = date(2025, 7, 31)
period_report = await accounting_service.generate_period_report(start_date, end_date)

# Налоговый отчет за период
tax_report = await accounting_service.generate_tax_report(period_id=current_period.id)
```
