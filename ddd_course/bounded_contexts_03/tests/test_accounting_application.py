"""
Интеграционные тесты для прикладного слоя контекста учета.
"""

from datetime import date, datetime, timedelta
from decimal import Decimal
from uuid import uuid4

import pytest
from accounting.application import (
    AccountingApplicationService,
    CloseFinancialPeriodCommand,
    CreateInvoiceCommand,
    InvoiceItemDTO,
    IssueInvoiceCommand,
    IssueRefundCommand,
    ProcessPaymentCommand,
    RecordPaymentCommand,
)
from accounting.domain import (
    FinancialPeriod,
    FinancialPeriodStatus,
    Invoice,
    InvoiceItem,
    InvoiceStatus,
    Payment,
    PaymentMethod,
    PaymentStatus,
)
from accounting.infrastructure import (
    AccountingUnitOfWork,
    ConsoleEmailService,
    DummyPaymentGateway,
    SimpleFinancialReportGenerator,
)
from shared_kernel import EntityId, Money


class TestAccountingApplicationService:
    """Тесты для прикладного сервиса учета."""

    @pytest.fixture
    async def service(self):
        """Создает экземпляр сервиса для тестирования."""
        uow = AccountingUnitOfWork()
        payment_gateway = DummyPaymentGateway(success_rate=1.0)
        email_service = ConsoleEmailService()
        report_generator = SimpleFinancialReportGenerator(uow)

        return AccountingApplicationService(
            uow=uow,
            payment_gateway=payment_gateway,
            email_service=email_service,
            report_generator=report_generator,
        )

    async def test_create_invoice(self, service):
        """Тестирование создания счета."""
        # Подготовка
        guest_id = EntityId()
        command = CreateInvoiceCommand(
            guest_id=guest_id,
            items=[
                InvoiceItemDTO(
                    description="Номер на двоих",
                    quantity=Decimal("2"),
                    unit_price=Money(amount=Decimal("2500.00")),
                    tax_rate=Decimal("20"),
                    discount=Money(amount=Decimal("0.00")),
                )
            ],
            due_date=date.today() + timedelta(days=7),
            notes="Тестовый счет",
        )

        # Действие
        invoice = await service.create_invoice(
            guest_id=command.guest_id,
            items=command.items,
            due_date=command.due_date,
            notes=command.notes,
            metadata=command.metadata,
        )

        # Проверка
        assert invoice.guest_id == guest_id
        assert len(invoice.items) == 1
        assert invoice.due_date == command.due_date
        assert invoice.notes == "Тестовый счет"
        assert invoice.status == InvoiceStatus.DRAFT

        # Проверяем, что счет сохранен в репозитории
        saved_invoice = await service.uow.invoices.get_by_id(invoice.id)
        assert saved_invoice is not None
        assert saved_invoice.id == invoice.id

    async def test_issue_invoice(self, service):
        """Тестирование выставления счета."""
        # Подготовка - создаем черновик счета
        guest_id = EntityId()
        invoice = await service.create_invoice(
            guest_id=guest_id,
            items=[
                InvoiceItem(
                    description="Номер на двоих",
                    quantity=Decimal("2"),
                    unit_price=Money(amount=Decimal("2500.00")),
                    tax_rate=Decimal("20"),
                    discount=Money(amount=Decimal("0.00")),
                )
            ],
            due_date=date.today() + timedelta(days=7),
        )

        # Действие
        command = IssueInvoiceCommand(invoice_id=invoice.id)
        issued_invoice = await service.issue_invoice(command.invoice_id)

        # Проверка
        assert issued_invoice.status == InvoiceStatus.ISSUED
        assert issued_invoice.issue_date == date.today()

        # Проверяем, что изменения сохранены
        saved_invoice = await service.uow.invoices.get_by_id(invoice.id)
        assert saved_invoice.status == InvoiceStatus.ISSUED

    async def test_record_payment(self, service):
        """Тестирование регистрации платежа."""
        # Подготовка - создаем и выставляем счет
        invoice = await self._create_and_issue_test_invoice(service)

        # Действие
        command = RecordPaymentCommand(
            invoice_id=invoice.id,
            amount=Money(amount=Decimal("6000.00")),
            payment_method=PaymentMethod.CREDIT_CARD.value,
            notes="Тестовый платеж",
        )

        payment = await service.record_payment(
            invoice_id=command.invoice_id,
            amount=command.amount,
            payment_method=command.payment_method,
            transaction_id=command.transaction_id,
            notes=command.notes,
            process_online=True,
        )

        # Проверка
        assert payment.invoice_id == invoice.id
        assert payment.amount == command.amount
        assert payment.payment_method == PaymentMethod(command.payment_method)
        assert payment.status == PaymentStatus.COMPLETED
        assert payment.transaction_id is not None

        # Проверяем, что счет обновлен
        updated_invoice = await service.uow.invoices.get_by_id(invoice.id)
        assert updated_invoice.status == InvoiceStatus.PAID

    async def test_process_payment(self, service):
        """Тестирование обработки платежа."""
        # Подготовка - создаем и выставляем счет
        invoice = await self._create_and_issue_test_invoice(service)

        # Создаем ожидающий платеж
        payment = Payment(
            invoice_id=invoice.id,
            amount=Money(amount=Decimal("6000.00")),
            payment_method=PaymentMethod.CREDIT_CARD,
            status=PaymentStatus.PENDING,
        )
        await service.uow.payments.save(payment)

        # Действие
        command = ProcessPaymentCommand(payment_id=payment.id)
        processed_payment = await service.process_payment(command.payment_id)

        # Проверка
        assert processed_payment.status == PaymentStatus.COMPLETED
        assert processed_payment.processed_at is not None

        # Проверяем, что счет обновлен
        updated_invoice = await service.uow.invoices.get_by_id(invoice.id)
        assert updated_invoice.status == InvoiceStatus.PAID

    async def test_issue_refund(self, service):
        """Тестирование возврата средств."""
        # Подготовка - создаем оплаченный счет
        invoice = await self._create_and_issue_test_invoice(service)

        # Создаем завершенный платеж
        payment = Payment(
            invoice_id=invoice.id,
            amount=Money(amount=Decimal("6000.00")),
            payment_method=PaymentMethod.CREDIT_CARD,
            status=PaymentStatus.COMPLETED,
            transaction_id="TXN123456",
            processed_at=datetime.utcnow(),
        )
        await service.uow.payments.save(payment)

        # Обновляем статус счета на оплаченный
        invoice.status = InvoiceStatus.PAID
        await service.uow.invoices.save(invoice)

        # Действие
        command = IssueRefundCommand(
            payment_id=payment.id,
            amount=Money(amount=Decimal("3000.00")),
            reason="Возврат за отмену бронирования",
            process_online=True,
        )

        refund = await service.issue_refund(
            payment_id=command.payment_id,
            amount=command.amount,
            reason=command.reason,
            process_online=command.process_online,
        )

        # Проверка
        assert refund.amount == command.amount
        assert refund.status == PaymentStatus.REFUNDED
        assert refund.metadata["original_payment_id"] == str(payment.id)

        # Проверяем, что исходный платеж обновлен
        updated_payment = await service.uow.payments.get_by_id(payment.id)
        assert updated_payment.status == PaymentStatus.REFUNDED

        # Проверяем, что счет обновлен
        updated_invoice = await service.uow.invoices.get_by_id(invoice.id)
        assert updated_invoice.status == InvoiceStatus.PARTIALLY_PAID

    async def test_close_financial_period(self, service):
        """Тестирование закрытия финансового периода."""
        # Подготовка - создаем финансовый период
        period = FinancialPeriod(
            name="Июнь 2023",
            start_date=date(2023, 6, 1),
            end_date=date(2023, 6, 30),
            status=FinancialPeriodStatus.OPEN,
        )
        await service.uow.financial_periods.save(period)

        # Действие
        closed_by = EntityId()
        command = CloseFinancialPeriodCommand(period_id=period.id, closed_by=closed_by)

        closed_period = await service.close_financial_period(
            period_id=command.period_id, closed_by=command.closed_by
        )

        # Проверка
        assert closed_period.status == FinancialPeriodStatus.CLOSED
        assert closed_period.closed_at is not None
        assert closed_period.closed_by == closed_by

    async def _create_and_issue_test_invoice(self, service) -> Invoice:
        """Создает и выставляет тестовый счет."""
        # Создаем счет
        invoice = await service.create_invoice(
            guest_id=EntityId(),
            items=[
                InvoiceItem(
                    description="Номер на двоих",
                    quantity=Decimal("2"),
                    unit_price=Money(amount=Decimal("2500.00")),
                    tax_rate=Decimal("20"),
                    discount=Money(amount=Decimal("0.00")),
                )
            ],
            due_date=date.today() + timedelta(days=7),
        )

        # Выставляем счет
        invoice.issue()
        await service.uow.invoices.save(invoice)

        return invoice


class TestDummyPaymentGateway:
    """Тесты для заглушки платежного шлюза."""

    async def test_process_payment_success(self):
        """Тестирование успешной обработки платежа."""
        # Подготовка
        gateway = DummyPaymentGateway(success_rate=1.0)
        amount = Money(amount=Decimal("1000.00"))

        # Действие
        result = await gateway.process_payment(
            amount=amount,
            payment_method="credit_card",
            payment_details={"card_number": "4111111111111111"},
            metadata={"invoice_id": "123"},
        )

        # Проверка
        assert result["status"] == "completed"
        assert "transaction_id" in result
        assert result["amount"] == amount.amount

    async def test_process_payment_failure(self):
        """Тестирование неудачной обработки платежа."""
        # Подготовка
        gateway = DummyPaymentGateway(success_rate=0.0)
        amount = Money(amount=Decimal("1000.00"))

        # Действие
        result = await gateway.process_payment(
            amount=amount,
            payment_method="credit_card",
            payment_details={"card_number": "4111111111111111"},
            metadata={"invoice_id": "123"},
        )

        # Проверка
        assert result["status"] == "failed"

    async def test_process_refund(self):
        """Тестирование обработки возврата."""
        # Подготовка
        gateway = DummyPaymentGateway()

        # Действие
        result = await gateway.process_refund(
            payment_id="PAY123",
            amount=Money(amount=Decimal("500.00")),
            reason="Возврат за отмену",
        )

        # Проверка
        assert result["status"] == "completed"
        assert "refund_id" in result
        assert result["original_payment_id"] == "PAY123"

    async def test_get_payment_status(self):
        """Тестирование проверки статуса платежа."""
        # Подготовка
        gateway = DummyPaymentGateway()
        transaction_id = "TXN" + str(uuid4().hex[:7].upper())

        # Имитируем обработку платежа
        await gateway.process_payment(
            amount=Money(amount=Decimal("1000.00")),
            payment_method="credit_card",
            payment_details={"card_number": "4111111111111111"},
            metadata={"transaction_id": transaction_id},
        )

        # Действие
        status = await gateway.get_payment_status(transaction_id)

        # Проверка
        assert status["transaction_id"] == transaction_id
        assert status["status"] == "completed"


class TestSimpleFinancialReportGenerator:
    """Тесты для генератора финансовых отчетов."""

    async def test_generate_daily_report(self):
        """Тестирование генерации ежедневного отчета."""
        # Подготовка
        uow = AccountingUnitOfWork()

        # Создаем тестовые данные
        period = FinancialPeriod(
            name="Июнь 2023",
            start_date=date(2023, 6, 1),
            end_date=date(2023, 6, 30),
            status=FinancialPeriodStatus.OPEN,
        )
        await uow.financial_periods.save(period)

        generator = SimpleFinancialReportGenerator(uow)

        # Действие
        report_date = date(2023, 6, 15)
        report_data = await generator.generate_daily_report(report_date)

        # Проверка
        import json

        report = json.loads(report_data.decode("utf-8"))
        assert report["report_type"] == "daily"
        assert report["date"] == report_date.isoformat()
        assert len(report["periods"]) == 1
        assert report["periods"][0]["name"] == "Июнь 2023"

    async def test_generate_period_report(self):
        """Тестирование генерации отчета за период."""
        # Подготовка
        uow = AccountingUnitOfWork()

        # Создаем тестовые данные
        period1 = FinancialPeriod(
            name="Июнь 2023",
            start_date=date(2023, 6, 1),
            end_date=date(2023, 6, 30),
            status=FinancialPeriodStatus.CLOSED,
        )
        period2 = FinancialPeriod(
            name="Июль 2023",
            start_date=date(2023, 7, 1),
            end_date=date(2023, 7, 31),
            status=FinancialPeriodStatus.OPEN,
        )

        await uow.financial_periods.save(period1)
        await uow.financial_periods.save(period2)

        generator = SimpleFinancialReportGenerator(uow)

        # Действие
        start_date = date(2023, 6, 1)
        end_date = date(2023, 7, 31)
        report_data = await generator.generate_period_report(start_date, end_date)

        # Проверка
        import json

        report = json.loads(report_data.decode("utf-8"))
        assert report["report_type"] == "period"
        assert report["start_date"] == start_date.isoformat()
        assert report["end_date"] == end_date.isoformat()
        assert len(report["periods"]) == 2
        assert report["periods"][0]["name"] == "Июль 2023"
        assert report["periods"][1]["name"] == "Июнь 2023"

    async def test_generate_tax_report(self):
        """Тестирование генерации налогового отчета."""
        # Подготовка
        uow = AccountingUnitOfWork()

        # Создаем тестовый период
        period = FinancialPeriod(
            name="Квартал 2, 2023",
            start_date=date(2023, 4, 1),
            end_date=date(2023, 6, 30),
            status=FinancialPeriodStatus.CLOSED,
        )

        generator = SimpleFinancialReportGenerator(uow)

        # Действие
        report_data = await generator.generate_tax_report(period)

        # Проверка
        import json

        report = json.loads(report_data.decode("utf-8"))
        assert report["report_type"] == "tax"
        assert report["period"]["name"] == period.name
        assert report["period"]["start_date"] == period.start_date.isoformat()
        assert report["period"]["end_date"] == period.end_date.isoformat()
        assert report["period"]["status"] == period.status.value
