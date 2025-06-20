"""
Прикладной слой контекста учета.

Содержит DTO и прикладные сервисы для работы с финансами.
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field
from shared_kernel import EntityId, Money

from .domain import AccountingService as DomainAccountingService
from .domain import (
    FinancialPeriod,
    FinancialReport,
    Invoice,
    InvoiceItem,
    Payment,
    PaymentMethod,
    PaymentStatus,
)
from .infrastructure import (
    AccountingUnitOfWork,
    ConsoleEmailService,
    DummyPaymentGateway,
    SimpleFinancialReportGenerator,
)
from .interfaces import (
    IAccountingService,
    IAccountingUnitOfWork,
    IEmailService,
    IFinancialReportGenerator,
    IPaymentGateway,
)

# ===================================================================
# DTO (Data Transfer Objects)
# ===================================================================


class InvoiceItemDTO(BaseModel):
    """DTO для позиции в счете."""

    description: str
    quantity: Decimal = Field(..., gt=0)
    unit_price: Money
    tax_rate: Decimal = Field(0, ge=0, le=100)  # Процент налога
    discount: Money = Field(Money(amount=0))
    metadata: Dict[str, Any] = Field(default_factory=dict)


class InvoiceDTO(BaseModel):
    """DTO для счета."""

    id: EntityId
    number: str
    booking_id: Optional[EntityId] = None
    guest_id: EntityId
    issue_date: date
    due_date: date
    status: str
    items: List[InvoiceItemDTO]
    subtotal: Money
    tax_amount: Money
    discount_amount: Money
    total: Money
    currency: str
    notes: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_domain(cls, invoice: Invoice) -> "InvoiceDTO":
        """Создает DTO из доменной модели."""
        return cls(
            id=invoice.id,
            number=invoice.number,
            booking_id=invoice.booking_id,
            guest_id=invoice.guest_id,
            issue_date=invoice.issue_date,
            due_date=invoice.due_date,
            status=invoice.status.value,
            items=[
                InvoiceItemDTO(
                    description=item.description,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                    tax_rate=item.tax_rate,
                    discount=item.discount,
                    metadata=item.metadata,
                )
                for item in invoice.items
            ],
            subtotal=invoice.subtotal,
            tax_amount=invoice.tax_amount,
            discount_amount=invoice.discount_amount,
            total=invoice.total,
            currency=invoice.currency,
            notes=invoice.notes,
            metadata=invoice.metadata,
            created_at=invoice.created_at,
            updated_at=invoice.updated_at,
        )


class PaymentDTO(BaseModel):
    """DTO для платежа."""

    id: EntityId
    invoice_id: EntityId
    amount: Money
    payment_method: str
    transaction_id: Optional[str] = None
    status: str
    processed_at: Optional[datetime] = None
    notes: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_domain(cls, payment: Payment) -> "PaymentDTO":
        """Создает DTO из доменной модели."""
        return cls(
            id=payment.id,
            invoice_id=payment.invoice_id,
            amount=payment.amount,
            payment_method=payment.payment_method.value,
            transaction_id=payment.transaction_id,
            status=payment.status.value,
            processed_at=payment.processed_at,
            notes=payment.notes,
            metadata=payment.metadata,
            created_at=payment.created_at,
            updated_at=payment.updated_at,
        )


class FinancialPeriodDTO(BaseModel):
    """DTO для финансового периода."""

    id: EntityId
    name: str
    start_date: date
    end_date: date
    status: str
    closed_at: Optional[datetime] = None
    closed_by: Optional[EntityId] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_domain(cls, period: FinancialPeriod) -> "FinancialPeriodDTO":
        """Создает DTO из доменной модели."""
        return cls(
            id=period.id,
            name=period.name,
            start_date=period.start_date,
            end_date=period.end_date,
            status=period.status.value,
            closed_at=period.closed_at,
            closed_by=period.closed_by,
            metadata=period.metadata,
            created_at=period.created_at,
            updated_at=period.updated_at,
        )


class FinancialReportDTO(BaseModel):
    """DTO для финансового отчета."""

    period: Dict[str, Any]
    metrics: Dict[str, Any]
    payment_methods: Dict[str, float]

    @classmethod
    def from_domain(cls, report: FinancialReport) -> "FinancialReportDTO":
        """Создает DTO из доменной модели."""
        return cls(
            period={
                "id": str(report.period.id),
                "name": report.period.name,
                "start_date": report.period.start_date.isoformat(),
                "end_date": report.period.end_date.isoformat(),
                "status": report.period.status.value,
            },
            metrics={
                "total_invoiced": report.total_invoiced.amount,
                "total_paid": report.total_paid.amount,
                "total_outstanding": report.total_outstanding.amount,
                "payment_methods_summary": {
                    method.value: amount.amount
                    for method, amount in report.payment_methods_summary.items()
                },
            },
            payment_methods={
                method.value: amount.amount
                for method, amount in report.payment_methods_summary.items()
            },
        )


# ===================================================================
# Команды (Commands) и запросы (Queries)
# ===================================================================


class CreateInvoiceCommand(BaseModel):
    """Команда создания счета."""

    guest_id: EntityId
    items: List[InvoiceItemDTO]
    due_date: date
    booking_id: Optional[EntityId] = None
    notes: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class IssueInvoiceCommand(BaseModel):
    """Команда выставления счета."""

    invoice_id: EntityId


class CancelInvoiceCommand(BaseModel):
    """Команда отмены счета."""

    invoice_id: EntityId
    reason: Optional[str] = None


class RecordPaymentCommand(BaseModel):
    """Команда регистрации платежа."""

    invoice_id: EntityId
    amount: Money
    payment_method: str
    transaction_id: Optional[str] = None
    notes: Optional[str] = None
    process_online: bool = False


class ProcessPaymentCommand(BaseModel):
    """Команда обработки платежа."""

    payment_id: EntityId


class IssueRefundCommand(BaseModel):
    """Команда возврата средств."""

    payment_id: EntityId
    amount: Optional[Money] = None
    reason: Optional[str] = None
    process_online: bool = False


class CloseFinancialPeriodCommand(BaseModel):
    """Команда закрытия финансового периода."""

    period_id: EntityId
    closed_by: EntityId


class GetInvoiceQuery(BaseModel):
    """Запрос на получение счета по идентификатору."""

    invoice_id: EntityId


class ListInvoicesQuery(BaseModel):
    """Запрос на получение списка счетов."""

    guest_id: Optional[EntityId] = None
    booking_id: Optional[EntityId] = None
    status: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    limit: int = 100
    offset: int = 0


class GetFinancialReportQuery(BaseModel):
    """Запрос на получение финансового отчета."""

    start_date: date
    end_date: date
    format: str = "json"


# ===================================================================
# Прикладные сервисы (Application Services)
# ===================================================================


class AccountingApplicationService(IAccountingService):
    """Прикладной сервис для работы с учетом."""

    def __init__(
        self,
        uow: IAccountingUnitOfWork,
        payment_gateway: IPaymentGateway,
        email_service: IEmailService,
        report_generator: IFinancialReportGenerator,
    ):
        self.uow = uow
        self.payment_gateway = payment_gateway
        self.email_service = email_service
        self.report_generator = report_generator
        self.domain_service = DomainAccountingService(uow.invoices)

    # ===============================================================
    # Методы для работы со счетами
    # ===============================================================

    async def create_invoice(
        self,
        guest_id: EntityId,
        items: List[InvoiceItem],
        due_date: date,
        booking_id: Optional[EntityId] = None,
        notes: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Invoice:
        """Создает новый счет."""
        try:
            # Создаем доменную модель счета
            invoice = self.domain_service.create_invoice(
                guest_id=guest_id,
                items=items,
                due_date=due_date,
                booking_id=booking_id,
                notes=notes,
                metadata=metadata or {},
            )

            # Сохраняем счет
            await self.uow.invoices.save(invoice)
            await self.uow.commit()

            return invoice

        except Exception:
            await self.uow.rollback()
            raise

    async def issue_invoice(self, invoice_id: EntityId) -> Invoice:
        """Выставляет счет (переводит в статус ISSUED)."""
        try:
            # Получаем счет
            invoice = await self.uow.invoices.get_by_id(invoice_id)
            if not invoice:
                raise ValueError(f"Счет с ID {invoice_id} не найден")

            # Выставляем счет
            invoice.issue()

            # Сохраняем изменения
            await self.uow.invoices.save(invoice)
            await self.uow.commit()

            # Отправляем уведомление (если настроено)
            if hasattr(self, "email_service"):
                await self.email_service.send_invoice(
                    to_email=invoice.customer_email or "",
                    invoice=invoice,
                    context={
                        "invoice": invoice,
                        "due_date": invoice.due_date.strftime("%d.%m.%Y"),
                        "total_amount": (
                            f"{invoice.total.amount:.2f} {invoice.currency}"
                        ),
                    },
                )

            return invoice

        except Exception:
            await self.uow.rollback()
            raise

    async def cancel_invoice(
        self, invoice_id: EntityId, reason: Optional[str] = None
    ) -> Invoice:
        """Аннулирует счет."""
        try:
            # Получаем счет
            invoice = await self.uow.invoices.get_by_id(invoice_id)
            if not invoice:
                raise ValueError(f"Счет с ID {invoice_id} не найден")

            # Аннулируем счет
            invoice.cancel(reason=reason)

            # Сохраняем изменения
            await self.uow.invoices.save(invoice)
            await self.uow.commit()

            return invoice

        except Exception:
            await self.uow.rollback()
            raise

    # ===============================================================
    # Методы для работы с платежами
    # ===============================================================

    async def record_payment(
        self,
        invoice_id: EntityId,
        amount: Money,
        payment_method: str,
        transaction_id: Optional[str] = None,
        notes: Optional[str] = None,
        process_online: bool = False,
    ) -> Payment:
        """Регистрирует платеж по счету."""
        try:
            # Получаем счет
            invoice = await self.uow.invoices.get_by_id(invoice_id)
            if not invoice:
                raise ValueError(f"Счет с ID {invoice_id} не найден")

            # Создаем платеж
            payment = Payment(
                invoice_id=invoice_id,
                amount=amount,
                payment_method=PaymentMethod(payment_method),
                transaction_id=transaction_id,
                notes=notes or "",
                status=PaymentStatus.PENDING,
            )

            # Если нужно обработать онлайн, отправляем в платежный шлюз
            if process_online:
                try:
                    # В реальном приложении здесь была бы интеграция с платежным шлюзом
                    result = await self.payment_gateway.process_payment(
                        amount=amount,
                        payment_method=payment_method,
                        payment_details={
                            "invoice_id": str(invoice_id),
                            "description": f"Оплата счета {invoice.number}",
                        },
                        metadata={
                            "invoice_id": str(invoice_id),
                            "guest_id": str(invoice.guest_id),
                        },
                    )

                    if result.get("status") == "completed":
                        payment.complete(transaction_id=result.get("transaction_id"))
                    else:
                        payment.fail(
                            reason=result.get("error_message", "Неизвестная ошибка")
                        )
                except Exception as e:
                    payment.fail(reason=str(e))

            # Сохраняем платеж
            await self.uow.payments.save(payment)

            # Обновляем статус счета, если платеж завершен
            if payment.status == PaymentStatus.COMPLETED:
                self.domain_service.apply_payment(invoice, payment)
                await self.uow.invoices.save(invoice)

            await self.uow.commit()

            # Отправляем уведомление (если настроено)
            if (
                hasattr(self, "email_service")
                and payment.status == PaymentStatus.COMPLETED
            ):
                if hasattr(self, "email_service"):
                    # TODO: Убедитесь, что у Invoice есть customer_email.
                    customer_email = getattr(
                        invoice, "customer_email", "default_customer@example.com"
                    )
                    await self.email_service.send_payment_confirmation(
                        to_email=customer_email or "default_customer@example.com",
                        payment=payment,
                        context={
                            "payment": PaymentDTO.from_domain(payment),
                            "invoice": InvoiceDTO.from_domain(invoice),
                            "invoice_number": invoice.number,
                        },
                    )

            return payment

        except Exception:
            await self.uow.rollback()
            raise

    async def process_payment(self, payment_id: EntityId) -> Payment:
        """Обрабатывает ожидающий платеж."""
        try:
            # Получаем платеж
            payment = await self.uow.payments.get_by_id(payment_id)
            if not payment:
                raise ValueError(f"Платеж с ID {payment_id} не найден")

            if payment.status != PaymentStatus.PENDING:
                raise ValueError("Можно обработать только ожидающий платеж")

            # Получаем счет
            invoice = await self.uow.invoices.get_by_id(payment.invoice_id)
            if not invoice:
                raise ValueError(f"Счет с ID {payment.invoice_id} не найден")

            # Обрабатываем платеж через платежный шлюз
            try:
                # В реальном приложении здесь была бы интеграция с платежным шлюзом
                result = await self.payment_gateway.process_payment(
                    amount=payment.amount,
                    payment_method=payment.payment_method.value,
                    payment_details={
                        "invoice_id": str(payment.invoice_id),
                        "description": f"Оплата счета {getattr(invoice, 'number', '')}",
                    },
                    metadata={
                        "payment_id": str(payment_id),
                        "invoice_id": str(payment.invoice_id),
                        "guest_id": str(getattr(invoice, "guest_id", "")),
                    },
                )

                if result.get("status") == "completed":
                    payment.complete(transaction_id=result.get("transaction_id"))

                    # Обновляем статус счета
                    self.domain_service.apply_payment(invoice, payment)
                    await self.uow.invoices.save(invoice)
                else:
                    payment.fail(
                        reason=result.get("error_message", "Неизвестная ошибка")
                    )

            except Exception as e:
                payment.fail(reason=str(e))

            # Сохраняем изменения
            await self.uow.payments.save(payment)
            await self.uow.commit()

            # Отправляем уведомление (если настроено)
            if (
                hasattr(self, "email_service")
                and payment.status == PaymentStatus.COMPLETED
            ):
                await self.email_service.send_payment_confirmation(
                    to_email=getattr(invoice, "customer_email", ""),
                    payment=payment,
                    context={
                        "invoice": invoice,
                        "payment": payment,
                        "payment_date": payment.processed_at.strftime("%d.%m.%Y %H:%M")
                        if payment.processed_at
                        else "",
                        "amount": (
                            f"{payment.amount.amount:.2f} {payment.amount.currency}"
                        ),
                    },
                )

            return payment

        except Exception:
            await self.uow.rollback()
            raise

    async def issue_refund(
        self,
        payment_id: EntityId,
        amount: Optional[Money] = None,
        reason: Optional[str] = None,
        process_online: bool = False,
    ) -> Payment:
        """Выполняет возврат средств."""
        try:
            # Получаем исходный платеж
            original_payment = await self.uow.payments.get_by_id(payment_id)
            if not original_payment:
                raise ValueError(f"Платеж с ID {payment_id} не найден")

            if original_payment.status != PaymentStatus.COMPLETED:
                raise ValueError("Можно вернуть только завершенный платеж")

            # Получаем счет
            invoice = await self.uow.invoices.get_by_id(original_payment.invoice_id)
            if not invoice:
                raise ValueError(f"Счет с ID {original_payment.invoice_id} не найден")

            # Создаем возврат
            refund = original_payment.refund(amount=amount, reason=reason)

            # Если нужно обработать онлайн, отправляем в платежный шлюз
            if process_online and original_payment.transaction_id:
                try:
                    # В реальном приложении здесь была бы интеграция с платежным шлюзом
                    result = await self.payment_gateway.process_refund(
                        payment_id=original_payment.transaction_id,
                        amount=amount,
                        reason=reason,
                        metadata={
                            "invoice_id": str(original_payment.invoice_id),
                            "guest_id": str(getattr(invoice, "guest_id", "")),
                            "original_payment_id": str(payment_id),
                        },
                    )

                    if result.get("status") != "completed":
                        refund.fail(
                            reason=result.get("error_message", "Неизвестная ошибка")
                        )

                except Exception as e:
                    refund.fail(reason=str(e))

            # Сохраняем возврат
            await self.uow.payments.save(refund)

            # Обновляем статус исходного платежа
            original_payment.status = PaymentStatus.REFUNDED
            await self.uow.payments.save(original_payment)

            # Обновляем статус счета
            self.domain_service.apply_payment(invoice, refund)
            await self.uow.invoices.save(invoice)

            await self.uow.commit()

            return refund

        except Exception:
            await self.uow.rollback()
            raise

    # ===============================================================
    # Методы для работы с финансовыми периодами
    # ===============================================================

    async def close_financial_period(
        self, period_id: EntityId, closed_by: EntityId
    ) -> FinancialPeriod:
        """Закрывает финансовый период."""
        try:
            # Получаем период
            period = await self.uow.financial_periods.get_by_id(period_id)
            if not period:
                raise ValueError(f"Финансовый период с ID {period_id} не найден")

            # Закрываем период
            period.close(closed_by=closed_by)

            # Сохраняем изменения
            await self.uow.financial_periods.save(period)
            await self.uow.commit()

            return period

        except Exception:
            await self.uow.rollback()
            raise

    # ===============================================================
    # Методы для генерации отчетов
    # ===============================================================

    async def generate_financial_report(
        self, start_date: date, end_date: date, format: str = "json"
    ) -> bytes:
        """Генерирует финансовый отчет за указанный период."""
        # Делегируем генерацию отчета компоненту report_generator
        try:
            report_bytes = await self.report_generator.generate_period_report(
                start_date=start_date, end_date=end_date, format=format
            )
            return report_bytes
        except Exception as e:
            # Здесь можно добавить логирование ошибки
            # self.logger.error(f"Error generating financial report: {e}")
            raise ValueError(f"Не удалось сгенерировать отчет: {e}")


# ===================================================================
# Фабрики для создания сервисов
# ===================================================================


def create_accounting_service(
    uow: Optional[IAccountingUnitOfWork] = None,
    payment_gateway: Optional[IPaymentGateway] = None,
    email_service: Optional[IEmailService] = None,
    report_generator: Optional[IFinancialReportGenerator] = None,
) -> AccountingApplicationService:
    """Создает экземпляр прикладного сервиса учета."""
    if uow is None:
        uow = AccountingUnitOfWork()

    if payment_gateway is None:
        payment_gateway = DummyPaymentGateway()

    if email_service is None:
        email_service = ConsoleEmailService()

    if report_generator is None:
        report_generator = SimpleFinancialReportGenerator(uow)

    return AccountingApplicationService(
        uow=uow,
        payment_gateway=payment_gateway,
        email_service=email_service,
        report_generator=report_generator,
    )
