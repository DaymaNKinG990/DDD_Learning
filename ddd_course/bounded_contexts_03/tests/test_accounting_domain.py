"""
Тесты для доменной модели контекста учета.
"""
import pytest
from datetime import date, datetime, timedelta
from decimal import Decimal
from uuid import uuid4, UUID

from shared_kernel import EntityId, Money
from accounting.domain import (
    Invoice,
    InvoiceStatus,
    InvoiceItem,
    Payment,
    PaymentStatus,
    PaymentMethod,
    FinancialPeriod,
    FinancialPeriodStatus,
    AccountingService
)


class TestInvoice:
    """Тесты для класса Invoice."""
    
    def test_create_invoice(self):
        """Тестирование создания счета."""
        # Подготовка
        guest_id = EntityId()
        items = [
            InvoiceItem(
                description="Номер на двоих",
                quantity=Decimal("2"),
                unit_price=Money(amount=Decimal("2500.00")),
                tax_rate=Decimal("20"),
                discount=Money(amount=Decimal("0.00"))
            )
        ]
        due_date = date.today() + timedelta(days=7)
        
        # Действие
        invoice = Invoice(
            guest_id=guest_id,
            items=items,
            due_date=due_date,
            subtotal=Money(amount=Decimal("5000.00")),
            tax_amount=Money(amount=Decimal("1000.00")),
            discount_amount=Money(amount=Decimal("0.00")),
            total=Money(amount=Decimal("6000.00"))
        )
        
        # Проверка
        assert invoice.guest_id == guest_id
        assert len(invoice.items) == 1
        assert invoice.due_date == due_date
        assert invoice.status == InvoiceStatus.DRAFT
        assert invoice.subtotal.amount == Decimal("5000.00")
        assert invoice.tax_amount.amount == Decimal("1000.00")
        assert invoice.total.amount == Decimal("6000.00")
    
    def test_issue_invoice(self):
        """Тестирование выставления счета."""
        # Подготовка
        invoice = self._create_test_invoice()
        
        # Действие
        invoice.issue()
        
        # Проверка
        assert invoice.status == InvoiceStatus.ISSUED
        assert invoice.issue_date == date.today()
    
    def test_cancel_invoice(self):
        """Тестирование отмены счета."""
        # Подготовка
        invoice = self._create_test_issued_invoice()
        reason = "Ошибка при создании"
        
        # Действие
        invoice.cancel(reason=reason)
        
        # Проверка
        assert invoice.status == InvoiceStatus.CANCELLED
        assert invoice.notes == f"Аннулирован. Причина: {reason}"
    
    def test_cancel_paid_invoice_fails(self):
        """Попытка отменить оплаченный счет должна вызывать исключение."""
        # Подготовка
        invoice = self._create_test_issued_invoice()
        invoice.status = InvoiceStatus.PAID
        
        # Проверка
        with pytest.raises(ValueError, match="Невозможно аннулировать счет в текущем статусе"):
            invoice.cancel()
    
    def _create_test_invoice(self) -> Invoice:
        """Создает тестовый счет в статусе DRAFT."""
        return Invoice(
            guest_id=EntityId(),
            items=[
                InvoiceItem(
                    description="Номер на двоих",
                    quantity=Decimal("2"),
                    unit_price=Money(amount=Decimal("2500.00")),
                    tax_rate=Decimal("20"),
                    discount=Money(amount=Decimal("0.00"))
                )
            ],
            due_date=date.today() + timedelta(days=7),
            subtotal=Money(amount=Decimal("5000.00")),
            tax_amount=Money(amount=Decimal("1000.00")),
            discount_amount=Money(amount=Decimal("0.00")),
            total=Money(amount=Decimal("6000.00"))
        )
    
    def _create_test_issued_invoice(self) -> Invoice:
        """Создает тестовый счет в статусе ISSUED."""
        invoice = self._create_test_invoice()
        invoice.issue()
        return invoice


class TestPayment:
    """Тесты для класса Payment."""
    
    def test_create_payment(self):
        """Тестирование создания платежа."""
        # Подготовка
        invoice_id = EntityId()
        amount = Money(amount=Decimal("6000.00"))
        payment_method = PaymentMethod.CREDIT_CARD
        
        # Действие
        payment = Payment(
            invoice_id=invoice_id,
            amount=amount,
            payment_method=payment_method
        )
        
        # Проверка
        assert payment.invoice_id == invoice_id
        assert payment.amount == amount
        assert payment.payment_method == payment_method
        assert payment.status == PaymentStatus.PENDING
    
    def test_complete_payment(self):
        """Тестирование завершения платежа."""
        # Подготовка
        payment = self._create_test_payment()
        transaction_id = "TXN123456"
        
        # Действие
        payment.complete(transaction_id=transaction_id)
        
        # Проверка
        assert payment.status == PaymentStatus.COMPLETED
        assert payment.transaction_id == transaction_id
        assert payment.processed_at is not None
    
    def test_fail_payment(self):
        """Тестирование отметки о неудачном платеже."""
        # Подготовка
        payment = self._create_test_payment()
        reason = "Недостаточно средств"
        
        # Действие
        payment.fail(reason=reason)
        
        # Проверка
        assert payment.status == PaymentStatus.FAILED
        assert payment.notes == f"Ошибка: {reason}"
        assert payment.processed_at is not None
    
    def test_refund_payment(self):
        """Тестирование создания возврата платежа."""
        # Подготовка
        payment = self._create_test_payment()
        payment.complete(transaction_id="TXN123456")
        refund_amount = Money(amount=Decimal("3000.00"))
        reason = "Возврат за отмену бронирования"
        
        # Действие
        refund = payment.refund(amount=refund_amount, reason=reason)
        
        # Проверка
        assert refund.amount == refund_amount
        assert refund.status == PaymentStatus.REFUNDED
        assert refund.notes == f"Возврат платежа {payment.id}. Причина: {reason}"
        assert refund.metadata["original_payment_id"] == str(payment.id)
    
    def _create_test_payment(self) -> Payment:
        """Создает тестовый платеж."""
        return Payment(
            invoice_id=EntityId(),
            amount=Money(amount=Decimal("6000.00")),
            payment_method=PaymentMethod.CREDIT_CARD
        )


class TestFinancialPeriod:
    """Тесты для класса FinancialPeriod."""
    
    def test_create_period(self):
        """Тестирование создания финансового периода."""
        # Подготовка
        name = "Июнь 2023"
        start_date = date(2023, 6, 1)
        end_date = date(2023, 6, 30)
        
        # Действие
        period = FinancialPeriod(
            name=name,
            start_date=start_date,
            end_date=end_date
        )
        
        # Проверка
        assert period.name == name
        assert period.start_date == start_date
        assert period.end_date == end_date
        assert period.status == FinancialPeriodStatus.OPEN
    
    def test_close_period(self):
        """Тестирование закрытия финансового периода."""
        # Подготовка
        period = self._create_test_period()
        closed_by = EntityId()
        
        # Действие
        period.close(closed_by=closed_by)
        
        # Проверка
        assert period.status == FinancialPeriodStatus.CLOSED
        assert period.closed_at is not None
        assert period.closed_by == closed_by
    
    def test_lock_period(self):
        """Тестирование блокировки финансового периода."""
        # Подготовка
        period = self._create_test_period()
        
        # Действие
        period.lock()
        
        # Проверка
        assert period.status == FinancialPeriodStatus.LOCKED
    
    def test_unlock_period(self):
        """Тестирование разблокировки финансового периода."""
        # Подготовка
        period = self._create_test_period()
        period.lock()
        
        # Действие
        period.unlock()
        
        # Проверка
        assert period.status == FinancialPeriodStatus.OPEN
    
    def test_archive_period(self):
        """Тестирование архивации финансового периода."""
        # Подготовка
        period = self._create_test_period()
        period.close(closed_by=EntityId())
        
        # Действие
        period.archive()
        
        # Проверка
        assert period.status == FinancialPeriodStatus.ARCHIVED
    
    def test_archive_open_period_fails(self):
        """Попытка архивировать открытый период должна вызывать исключение."""
        # Подготовка
        period = self._create_test_period()
        
        # Проверка
        with pytest.raises(ValueError, match="Невозможно архивировать незакрытый период"):
            period.archive()
    
    def _create_test_period(self) -> FinancialPeriod:
        """Создает тестовый финансовый период."""
        return FinancialPeriod(
            name="Июнь 2023",
            start_date=date(2023, 6, 1),
            end_date=date(2023, 6, 30)
        )


class TestAccountingService:
    """Тесты для сервиса учета."""
    
    def test_create_invoice(self):
        """Тестирование создания счета через сервис."""
        # Подготовка
        invoice_repo = MockInvoiceRepository()
        service = AccountingService(invoice_repo)
        
        guest_id = EntityId()
        items = [
            InvoiceItem(
                description="Номер на двоих",
                quantity=Decimal("2"),
                unit_price=Money(amount=Decimal("2500.00")),
                tax_rate=Decimal("20"),
                discount=Money(amount=Decimal("0.00"))
            )
        ]
        due_date = date.today() + timedelta(days=7)
        
        # Действие
        invoice = service.create_invoice(
            guest_id=guest_id,
            items=items,
            due_date=due_date
        )
        
        # Проверка
        assert invoice.guest_id == guest_id
        assert len(invoice.items) == 1
        assert invoice.due_date == due_date
        assert invoice.status == InvoiceStatus.DRAFT
        assert len(invoice_repo.saved_invoices) == 1
        assert invoice_repo.saved_invoices[0] == invoice


# Вспомогательные классы для тестирования

class MockInvoiceRepository:
    """Мок-репозиторий для тестирования."""
    
    def __init__(self):
        self.saved_invoices = []
    
    async def save(self, invoice: Invoice) -> None:
        """Сохраняет счет."""
        self.saved_invoices.append(invoice)
