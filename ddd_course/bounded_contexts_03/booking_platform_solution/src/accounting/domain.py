"""
Доменная модель контекста учета.

Содержит основные сущности, агрегаты и доменные сервисы
для управления финансовыми операциями.
"""
from datetime import datetime, date
from decimal import Decimal
from enum import Enum
from typing import List, Optional, Dict, Any, Set, Tuple
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, validator, root_validator

from shared_kernel import EntityId, DomainEvent, DomainException, Money


class InvoiceStatus(str, Enum):
    """Статусы счета."""
    DRAFT = "draft"          # Черновик
    ISSUED = "issued"        # Выставлен
    PARTIALLY_PAID = "partially_paid"  # Частично оплачен
    PAID = "paid"            # Оплачен
    OVERDUE = "overdue"      # Просрочен
    CANCELLED = "cancelled"  # Аннулирован


class PaymentStatus(str, Enum):
    """Статусы платежа."""
    PENDING = "pending"      # Ожидает обработки
    COMPLETED = "completed"  # Завершен
    FAILED = "failed"        # Неудачный
    REFUNDED = "refunded"    # Возвращен
    CANCELLED = "cancelled"  # Отменен


class PaymentMethod(str, Enum):
    """Методы оплаты."""
    CASH = "cash"                # Наличные
    CREDIT_CARD = "credit_card"   # Кредитная карта
    BANK_TRANSFER = "bank_transfer"  # Банковский перевод
    ONLINE_PAYMENT = "online_payment"  # Онлайн-оплата
    OTHER = "other"              # Другой способ


class TransactionType(str, Enum):
    """Типы транзакций."""
    PAYMENT = "payment"        # Платеж
    REFUND = "refund"          # Возврат
    ADJUSTMENT = "adjustment"  # Корректировка
    TAX = "tax"                # Налог
    DISCOUNT = "discount"      # Скидка
    SERVICE_FEE = "service_fee"  # Сервисный сбор
    OTHER = "other"            # Прочее


class FinancialPeriodStatus(str, Enum):
    """Статусы финансового периода."""
    OPEN = "open"          # Открыт
    CLOSED = "closed"      # Закрыт
    LOCKED = "locked"      # Заблокирован (изменения запрещены)
    ARCHIVED = "archived"  # Архивирован


class InvoiceItem(BaseModel):
    """Позиция в счете."""
    id: EntityId = Field(default_factory=uuid4)
    description: str
    quantity: Decimal = Field(..., gt=0)
    unit_price: Money
    tax_rate: Decimal = Field(0, ge=0, le=100)  # Процент налога
    discount: Money = Field(Money(amount=0))
    total: Money
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @root_validator(pre=True)
    def calculate_total(cls, values):
        """Вычисляет общую сумму позиции с учетом скидки и налога."""
        if 'total' in values and values['total'] is not None:
            return values
            
        quantity = Decimal(str(values.get('quantity', 1)))
        unit_price = values.get('unit_price')
        tax_rate = Decimal(str(values.get('tax_rate', 0)))
        discount = values.get('discount', Money(amount=0))
        
        if not unit_price:
            raise ValueError("unit_price is required")
        
        subtotal = unit_price * quantity - discount
        tax = subtotal * (tax_rate / 100)
        total = subtotal + tax
        
        values['total'] = total
        return values


class Invoice(DomainEvent):
    """Счет на оплату."""
    id: EntityId = Field(default_factory=uuid4)
    number: str  # Уникальный номер счета
    booking_id: Optional[EntityId] = None
    guest_id: EntityId
    issue_date: date = Field(default_factory=date.today)
    due_date: date
    status: InvoiceStatus = InvoiceStatus.DRAFT
    items: List[InvoiceItem] = Field(default_factory=list)
    subtotal: Money
    tax_amount: Money
    discount_amount: Money = Field(Money(amount=0))
    total: Money
    currency: str = "RUB"
    notes: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    @root_validator(pre=True)
    def calculate_totals(cls, values):
        """Вычисляет промежуточные итоги и общую сумму счета."""
        if 'subtotal' in values and 'total' in values and 'tax_amount' in values:
            return values
            
        items = values.get('items', [])
        if not items:
            values['subtotal'] = Money(amount=0)
            values['tax_amount'] = Money(amount=0)
            values['total'] = Money(amount=0)
            return values
        
        subtotal = Money(amount=0)
        tax_amount = Money(amount=0)
        discount_amount = Money(amount=0)
        
        for item in items:
            if not isinstance(item, InvoiceItem):
                continue
                
            item_subtotal = item.unit_price * item.quantity - item.discount
            item_tax = item_subtotal * (item.tax_rate / 100)
            
            subtotal += item.unit_price * item.quantity
            tax_amount += item_tax
            discount_amount += item.discount
        
        total = subtount - discount_amount + tax_amount
        
        values['subtotal'] = subtotal
        values['tax_amount'] = tax_amount
        values['discount_amount'] = discount_amount
        values['total'] = total
        
        return values
    
    def add_item(self, item: InvoiceItem) -> None:
        """Добавляет позицию в счет."""
        if self.status != InvoiceStatus.DRAFT:
            raise DomainException("Невозможно изменить счет в текущем статусе")
            
        self.items.append(item)
        self._recalculate_totals()
        self.updated_at = datetime.utcnow()
    
    def remove_item(self, item_id: EntityId) -> None:
        """Удаляет позицию из счета."""
        if self.status != InvoiceStatus.DRAFT:
            raise DomainException("Невозможно изменить счет в текущем статусе")
            
        self.items = [item for item in self.items if item.id != item_id]
        self._recalculate_totals()
        self.updated_at = datetime.utcnow()
    
    def issue(self) -> None:
        """Выставляет счет (переводит в статус ISSUED)."""
        if self.status != InvoiceStatus.DRAFT:
            raise DomainException("Счет уже выставлен или аннулирован")
            
        if not self.items:
            raise DomainException("Невозможно выставить пустой счет")
            
        self.status = InvoiceStatus.ISSUED
        self.updated_at = datetime.utcnow()
    
    def cancel(self, reason: Optional[str] = None) -> None:
        """Аннулирует счет."""
        if self.status in (InvoiceStatus.PAID, InvoiceStatus.CANCELLED):
            raise DomainException("Невозможно аннулировать счет в текущем статусе")
            
        self.status = InvoiceStatus.CANCELLED
        self.notes = f"{self.notes or ''}\nАннулирован. Причина: {reason or 'не указана'}"
        self.updated_at = datetime.utcnow()
    
    def _recalculate_totals(self) -> None:
        """Пересчитывает итоговые суммы счета."""
        subtotal = Money(amount=0)
        tax_amount = Money(amount=0)
        discount_amount = Money(amount=0)
        
        for item in self.items:
            item_subtotal = item.unit_price * item.quantity - item.discount
            item_tax = item_subtotal * (item.tax_rate / 100)
            
            subtotal += item.unit_price * item.quantity
            tax_amount += item_tax
            discount_amount += item.discount
        
        self.subtotal = subtotal
        self.tax_amount = tax_amount
        self.discount_amount = discount_amount
        self.total = subtotal - discount_amount + tax_amount


class Payment(DomainEvent):
    """Платеж."""
    id: EntityId = Field(default_factory=uuid4)
    invoice_id: EntityId
    amount: Money
    payment_method: PaymentMethod
    transaction_id: Optional[str] = None  # Внешний идентификатор транзакции
    status: PaymentStatus = PaymentStatus.PENDING
    processed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    def complete(self, transaction_id: Optional[str] = None) -> None:
        """Отмечает платеж как завершенный."""
        if self.status != PaymentStatus.PENDING:
            raise DomainException("Платеж уже обработан")
            
        self.status = PaymentStatus.COMPLETED
        self.processed_at = datetime.utcnow()
        if transaction_id:
            self.transaction_id = transaction_id
        self.updated_at = datetime.utcnow()
    
    def fail(self, reason: Optional[str] = None) -> None:
        """Отмечает платеж как неудачный."""
        if self.status != PaymentStatus.PENDING:
            raise DomainException("Платеж уже обработан")
            
        self.status = PaymentStatus.FAILED
        self.processed_at = datetime.utcnow()
        self.notes = f"{self.notes or ''}\nОшибка: {reason or 'не указана'}"
        self.updated_at = datetime.utcnow()
    
    def refund(self, amount: Optional[Money] = None, reason: Optional[str] = None) -> 'Payment':
        """Создает возврат средств."""
        if self.status != PaymentStatus.COMPLETED:
            raise DomainException("Невозможно вернуть необработанный платеж")
            
        refund_amount = amount or self.amount
        if refund_amount > self.amount:
            raise DomainException("Сумма возврата не может превышать сумму платежа")
            
        refund = Payment(
            invoice_id=self.invoice_id,
            amount=refund_amount,
            payment_method=self.payment_method,
            status=PaymentStatus.REFUNDED,
            notes=f"Возврат платежа {self.id}. Причина: {reason or 'не указана'}",
            metadata={"original_payment_id": str(self.id)}
        )
        
        return refund


class FinancialPeriod(BaseModel):
    """Финансовый период (например, день, месяц, квартал)."""
    id: EntityId = Field(default_factory=uuid4)
    name: str
    start_date: date
    end_date: date
    status: FinancialPeriodStatus = FinancialPeriodStatus.OPEN
    closed_at: Optional[datetime] = None
    closed_by: Optional[EntityId] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    @validator('end_date')
    def end_date_after_start_date(cls, v, values):
        if 'start_date' in values and v < values['start_date']:
            raise ValueError('Дата окончания должна быть позже даты начала')
        return v
    
    def close(self, closed_by: EntityId) -> None:
        """Закрывает финансовый период."""
        if self.status != FinancialPeriodStatus.OPEN:
            raise DomainException("Период уже закрыт или заблокирован")
            
        self.status = FinancialPeriodStatus.CLOSED
        self.closed_at = datetime.utcnow()
        self.closed_by = closed_by
        self.updated_at = datetime.utcnow()
    
    def lock(self) -> None:
        """Блокирует период для изменений."""
        if self.status != FinancialPeriodStatus.OPEN:
            raise DomainException("Период уже закрыт или заблокирован")
            
        self.status = FinancialPeriodStatus.LOCKED
        self.updated_at = datetime.utcnow()
    
    def unlock(self) -> None:
        """Разблокирует период для изменений."""
        if self.status != FinancialPeriodStatus.LOCKED:
            raise DomainException("Период не заблокирован")
            
        self.status = FinancialPeriodStatus.OPEN
        self.updated_at = datetime.utcnow()
    
    def archive(self) -> None:
        """Архивирует период."""
        if self.status != FinancialPeriodStatus.CLOSED:
            raise DomainException("Невозможно архивировать незакрытый период")
            
        self.status = FinancialPeriodStatus.ARCHIVED
        self.updated_at = datetime.utcnow()


class AccountingService:
    """Доменный сервис для учета финансовых операций."""
    
    def __init__(self, invoice_repository: 'IInvoiceRepository'):
        self.invoice_repository = invoice_repository
    
    def create_invoice(
        self,
        guest_id: EntityId,
        due_date: date,
        items: List[InvoiceItem],
        booking_id: Optional[EntityId] = None,
        notes: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Invoice:
        """Создает новый счет."""
        invoice = Invoice(
            guest_id=guest_id,
            booking_id=booking_id,
            due_date=due_date,
            items=items,
            notes=notes or "",
            metadata=metadata or {}
        )
        
        # Генерируем номер счета (в реальном приложении может быть более сложная логика)
        invoice.number = f"INV-{datetime.utcnow().strftime('%Y%m%d')}-{str(invoice.id)[:8].upper()}"
        
        return invoice
    
    def record_payment(
        self,
        invoice: Invoice,
        amount: Money,
        payment_method: PaymentMethod,
        transaction_id: Optional[str] = None,
        notes: Optional[str] = None
    ) -> Payment:
        """Регистрирует платеж по счету."""
        if invoice.status == InvoiceStatus.CANCELLED:
            raise DomainException("Невозможно принять оплату по аннулированному счету")
            
        if invoice.status == InvoiceStatus.PAID and invoice.total.amount > 0:
            raise DomainException("Счет уже полностью оплачен")
            
        payment = Payment(
            invoice_id=invoice.id,
            amount=amount,
            payment_method=payment_method,
            transaction_id=transaction_id,
            notes=notes or ""
        )
        
        # В реальном приложении здесь была бы интеграция с платежным шлюзом
        # и обработка ответа
        
        return payment
    
    def apply_payment(self, invoice: Invoice, payment: Payment) -> None:
        """Применяет платеж к счету."""
        if payment.status != PaymentStatus.COMPLETED:
            raise DomainException("Можно применить только завершенный платеж")
            
        # В реальном приложении здесь была бы логика обновления статуса счета
        # на основе суммы платежа и оставшейся суммы к оплате
        
        # Обновляем статус счета, если он полностью оплачен
        if invoice.total.amount <= 0 or self._is_invoice_paid(invoice):
            invoice.status = InvoiceStatus.PAID
        elif payment.amount > 0:
            invoice.status = InvoiceStatus.PARTIALLY_PAID
        
        invoice.updated_at = datetime.utcnow()
    
    def _is_invoice_paid(self, invoice: Invoice) -> bool:
        """Проверяет, полностью ли оплачен счет."""
        # В реальном приложении здесь была бы логика проверки всех платежей по счету
        # и сравнения с общей суммой
        return invoice.status == InvoiceStatus.PAID


class FinancialReport:
    """Финансовый отчет за период."""
    
    def __init__(
        self,
        period: FinancialPeriod,
        invoices: List[Invoice],
        payments: List[Payment]
    ):
        self.period = period
        self.invoices = invoices
        self.payments = payments
    
    @property
    def total_invoiced(self) -> Money:
        """Общая сумма выставленных счетов."""
        return sum((inv.total for inv in self.invoices), start=Money(amount=0))
    
    @property
    def total_paid(self) -> Money:
        """Общая сумма полученных платежей."""
        return sum(
            (p.amount for p in self.payments 
             if p.status == PaymentStatus.COMPLETED),
            start=Money(amount=0)
        )
    
    @property
    def total_outstanding(self) -> Money:
        """Общая сумма задолженности."""
        return self.total_invoiced - self.total_paid
    
    @property
    def payment_methods_summary(self) -> Dict[PaymentMethod, Money]:
        """Сводка по методам оплаты."""
        summary = {}
        for payment in self.payments:
            if payment.status == PaymentStatus.COMPLETED:
                if payment.payment_method not in summary:
                    summary[payment.payment_method] = Money(amount=0)
                summary[payment.payment_method] += payment.amount
        return summary
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразует отчет в словарь."""
        return {
            "period": {
                "id": str(self.period.id),
                "name": self.period.name,
                "start_date": self.period.start_date.isoformat(),
                "end_date": self.period.end_date.isoformat(),
                "status": self.period.status.value
            },
            "metrics": {
                "total_invoiced": self.total_invoiced.amount,
                "total_paid": self.total_paid.amount,
                "total_outstanding": self.total_outstanding.amount,
                "invoice_count": len(self.invoices),
                "payment_count": len([p for p in self.payments if p.status == PaymentStatus.COMPLETED])
            },
            "payment_methods": {
                method.value: amount.amount 
                for method, amount in self.payment_methods_summary.items()
            }
        }
