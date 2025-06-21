"""
Интерфейсы (порты) для контекста учета.
"""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING, Any, Dict, Protocol

from ..shared_kernel import EntityId, Money
from .domain import FinancialPeriod, Invoice, Payment

if TYPE_CHECKING:
    from booking.domain import BookingCreated, Room


class IInvoiceRepository(Protocol):
    """Интерфейс репозитория для счетов."""

    async def get_by_id(self, invoice_id: EntityId) -> Invoice | None: ...
    async def add(self, invoice: Invoice) -> None: ...
    async def save(self, invoice: Invoice) -> None: ...


class IRoomRepository(Protocol):
    """Интерфейс репозитория для комнат (в контексте учета)."""

    async def get_by_id(self, room_id: EntityId) -> Room | None: ...


class IPaymentRepository(Protocol):
    """Интерфейс репозитория для платежей."""

    async def get_by_id(self, payment_id: EntityId) -> Payment | None: ...
    async def save(self, payment: Payment) -> None: ...


class IFinancialPeriodRepository(Protocol):
    """Интерфейс репозитория для финансовых периодов."""

    async def get_by_id(self, period_id: EntityId) -> FinancialPeriod | None: ...
    async def save(self, period: FinancialPeriod) -> None: ...
    async def list_by_date_range(
        self, start_date: date, end_date: date, limit: int = 100, offset: int = 0
    ) -> list[FinancialPeriod]: ...


class IEmailService(Protocol):
    """Интерфейс для отправки email-уведомлений."""

    async def send_invoice(
        self, to_email: str, invoice: Invoice, context: Dict[str, Any]
    ) -> None: ...
    async def send_payment_confirmation(
        self, to_email: str, payment: Payment, context: Dict[str, Any]
    ) -> None: ...


class IPaymentGateway(Protocol):
    """Интерфейс для взаимодействия с платежным шлюзом."""

    async def process_payment(
        self,
        amount: Money,
        payment_method: str,
        payment_details: Dict[str, Any],
        metadata: Dict[str, Any],
    ) -> Dict[str, Any]: ...
    async def process_refund(
        self,
        payment_id: str,
        amount: Money | None,
        reason: str | None,
        metadata: Dict[str, Any],
    ) -> Dict[str, Any]: ...


class IFinancialReportGenerator(Protocol):
    """Интерфейс для генерации финансовых отчетов."""

    async def generate_period_report(
        self, start_date: date, end_date: date, format: str
    ) -> bytes: ...


class IAccountingService(Protocol):
    """Интерфейс сервиса для контекста Accounting."""

    async def create_invoice_for_booking(self, event: "BookingCreated") -> None: ...


class IAccountingUnitOfWork(Protocol):
    """Интерфейс Unit of Work для контекста Accounting."""

    invoices: IInvoiceRepository
    rooms: IRoomRepository
    payments: IPaymentRepository
    financial_periods: IFinancialPeriodRepository

    async def __aenter__(self) -> IAccountingUnitOfWork: ...
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None: ...
    async def commit(self) -> None: ...
    async def rollback(self) -> None: ...
