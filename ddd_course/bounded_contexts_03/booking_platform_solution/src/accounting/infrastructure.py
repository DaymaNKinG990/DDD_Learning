"""
Инфраструктурный слой контекста учета.

Содержит реализации репозиториев и сервисов,
а также другие инфраструктурные компоненты.
"""

import json
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional
from uuid import uuid4

from booking.infrastructure import (
    InMemoryRoomRepository as BookingRoomRepository,
)
from pydantic import Set
from shared_kernel import EntityId, Money

from .domain import (
    FinancialPeriod,
    FinancialPeriodStatus,
    Invoice,
    InvoiceStatus,
    Payment,
    PaymentStatus,
)
from .interfaces import (
    IAccountingUnitOfWork,
    IEmailService,
    IFinancialPeriodRepository,
    IFinancialReportGenerator,
    IInvoiceRepository,
    IPaymentGateway,
    IPaymentRepository,
    IRoomRepository,
)


class InMemoryInvoiceRepository(IInvoiceRepository):
    """In-memory реализация репозитория счетов."""

    def __init__(self) -> None:
        self._invoices: Dict[EntityId, Invoice] = {}
        self._invoices_by_number: Dict[str, Invoice] = {}
        self._invoices_by_guest: Dict[EntityId, Set[EntityId]] = {}
        self._invoices_by_booking: Dict[EntityId, Set[EntityId]] = {}

    async def get_by_id(self, invoice_id: EntityId) -> Optional[Invoice]:
        """Возвращает счет по идентификатору."""
        return self._invoices.get(invoice_id)

    async def add(self, invoice: Invoice) -> None:
        """Добавляет новый счет."""
        await self.save(invoice)

    async def get_by_number(self, number: str) -> Optional[Invoice]:
        """Возвращает счет по номеру."""
        return self._invoices_by_number.get(number)

    async def list_by_guest(
        self,
        guest_id: EntityId,
        status: Optional[InvoiceStatus] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Invoice]:
        """Возвращает список счетов гостя."""
        invoice_ids = self._invoices_by_guest.get(guest_id, set())
        result = []

        for inv_id in sorted(invoice_ids, reverse=True):
            invoice = self._invoices.get(inv_id)
            if invoice and (status is None or invoice.status == status):
                result.append(invoice)

        return result[offset : offset + limit]

    async def list_by_booking(
        self,
        booking_id: EntityId,
        status: Optional[InvoiceStatus] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Invoice]:
        """Возвращает список счетов по бронированию."""
        invoice_ids = self._invoices_by_booking.get(booking_id, set())
        result = []

        for inv_id in sorted(invoice_ids, reverse=True):
            invoice = self._invoices.get(inv_id)
            if invoice and (status is None or invoice.status == status):
                result.append(invoice)

        return result[offset : offset + limit]

    async def list_by_status(
        self, status: InvoiceStatus, limit: int = 100, offset: int = 0
    ) -> List[Invoice]:
        """Возвращает список счетов по статусу."""
        result = [inv for inv in self._invoices.values() if inv.status == status]
        result.sort(key=lambda x: x.issue_date, reverse=True)
        return result[offset : offset + limit]

    async def list_overdue(
        self, as_of_date: Optional[date] = None, limit: int = 100, offset: int = 0
    ) -> List[Invoice]:
        """Возвращает список просроченных счетов."""
        if as_of_date is None:
            as_of_date = date.today()

        result = [
            inv
            for inv in self._invoices.values()
            if inv.status in {InvoiceStatus.ISSUED, InvoiceStatus.PARTIALLY_PAID}
            and inv.due_date < as_of_date
        ]
        result.sort(key=lambda x: x.due_date)
        return result[offset : offset + limit]

    async def save(self, invoice: Invoice) -> None:
        """Сохраняет счет."""
        self._invoices[invoice.id] = invoice

        if hasattr(invoice, "number") and invoice.number:
            self._invoices_by_number[invoice.number] = invoice

        # Обновляем индексы
        if invoice.guest_id not in self._invoices_by_guest:
            self._invoices_by_guest[invoice.guest_id] = set()
        self._invoices_by_guest[invoice.guest_id].add(invoice.id)

        if invoice.booking_id:
            if invoice.booking_id not in self._invoices_by_booking:
                self._invoices_by_booking[invoice.booking_id] = set()
            self._invoices_by_booking[invoice.booking_id].add(invoice.id)

    async def delete(self, invoice_id: EntityId) -> bool:
        """Удаляет счет по идентификатору."""
        if invoice_id not in self._invoices:
            return False

        invoice = self._invoices[invoice_id]

        # Удаляем из индексов
        if invoice.guest_id in self._invoices_by_guest:
            self._invoices_by_guest[invoice.guest_id].discard(invoice_id)

        if invoice.booking_id and invoice.booking_id in self._invoices_by_booking:
            self._invoices_by_booking[invoice.booking_id].discard(invoice_id)

        if hasattr(invoice, "number") and invoice.number in self._invoices_by_number:
            del self._invoices_by_number[invoice.number]

        # Удаляем сам счет
        del self._invoices[invoice_id]
        return True


class InMemoryPaymentRepository(IPaymentRepository):
    """In-memory реализация репозитория платежей."""

    def __init__(self) -> None:
        self._payments: Dict[EntityId, Payment] = {}
        self._payments_by_invoice: Dict[EntityId, Set[EntityId]] = {}
        self._payments_by_guest: Dict[EntityId, Set[EntityId]] = {}

    async def get_by_id(self, payment_id: EntityId) -> Optional[Payment]:
        """Возвращает платеж по идентификатору."""
        return self._payments.get(payment_id)

    async def list_by_invoice(
        self,
        invoice_id: EntityId,
        status: Optional[PaymentStatus] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Payment]:
        """Возвращает список платежей по счету."""
        payment_ids = self._payments_by_invoice.get(invoice_id, set())
        result = []

        for pay_id in sorted(payment_ids, reverse=True):
            payment = self._payments.get(pay_id)
            if payment and (status is None or payment.status == status):
                result.append(payment)

        return result[offset : offset + limit]

    async def list_by_guest(
        self,
        guest_id: EntityId,
        status: Optional[PaymentStatus] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Payment]:
        """Возвращает список платежей гостя."""
        payment_ids = self._payments_by_guest.get(guest_id, set())
        result = []

        for pay_id in sorted(payment_ids, reverse=True):
            payment = self._payments.get(pay_id)
            if not payment:
                continue

            if status is not None and payment.status != status:
                continue

            if (
                start_date
                and payment.processed_at
                and payment.processed_at.date() < start_date
            ):
                continue

            if (
                end_date
                and payment.processed_at
                and payment.processed_at.date() > end_date
            ):
                continue

            result.append(payment)

        return result[offset : offset + limit]

    async def list_by_status(
        self,
        status: PaymentStatus,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Payment]:
        """Возвращает список платежей по статусу."""
        result = []

        for payment in sorted(
            self._payments.values(), key=lambda x: x.created_at, reverse=True
        ):
            if payment.status != status:
                continue

            if (
                start_date
                and payment.processed_at
                and payment.processed_at.date() < start_date
            ):
                continue

            if (
                end_date
                and payment.processed_at
                and payment.processed_at.date() > end_date
            ):
                continue

            result.append(payment)

        return result[offset : offset + limit]

    async def save(self, payment: Payment) -> None:
        """Сохраняет платеж."""
        self._payments[payment.id] = payment

        # Обновляем индексы
        if payment.invoice_id not in self._payments_by_invoice:
            self._payments_by_invoice[payment.invoice_id] = set()
        self._payments_by_invoice[payment.invoice_id].add(payment.id)

        # Примечание: для индексации по гостю нужен доп. запрос к репо счетов
        # В реальной реализации это можно оптимизировать


class InMemoryFinancialPeriodRepository(IFinancialPeriodRepository):
    """In-memory реализация репозитория финансовых периодов."""

    def __init__(self) -> None:
        self._periods: Dict[EntityId, FinancialPeriod] = {}
        self._periods_by_date: Dict[date, FinancialPeriod] = {}

    async def get_by_id(self, period_id: EntityId) -> Optional[FinancialPeriod]:
        """Возвращает финансовый период по идентификатору."""
        return self._periods.get(period_id)

    async def get_by_date(self, date: date) -> Optional[FinancialPeriod]:
        """Возвращает финансовый период, в который входит указанная дата."""
        for period in self._periods.values():
            if period.start_date <= date <= period.end_date:
                return period
        return None

    async def list_by_status(
        self, status: FinancialPeriodStatus, limit: int = 100, offset: int = 0
    ) -> List[FinancialPeriod]:
        """Возвращает список финансовых периодов по статусу."""
        result = [p for p in self._periods.values() if p.status == status]
        result.sort(key=lambda x: x.start_date, reverse=True)
        return result[offset : offset + limit]

    async def list_by_date_range(
        self, start_date: date, end_date: date, limit: int = 100, offset: int = 0
    ) -> List[FinancialPeriod]:
        """Возвращает список финансовых периодов в указанном диапазоне дат."""
        result = [
            p
            for p in self._periods.values()
            if not (p.end_date < start_date or p.start_date > end_date)
        ]
        result.sort(key=lambda x: x.start_date, reverse=True)
        return result[offset : offset + limit]

    async def get_current_period(self) -> Optional[FinancialPeriod]:
        """Возвращает текущий открытый финансовый период."""
        today = date.today()
        for period in self._periods.values():
            if (
                period.status == FinancialPeriodStatus.OPEN
                and period.start_date <= today <= period.end_date
            ):
                return period
        return None

    async def save(self, period: FinancialPeriod) -> None:
        """Сохраняет финансовый период."""
        self._periods[period.id] = period

        # Обновляем индекс по датам
        current_date = period.start_date
        while current_date <= period.end_date:
            self._periods_by_date[current_date] = period
            current_date += timedelta(days=1)


class AccountingUnitOfWork(IAccountingUnitOfWork):
    """Единица работы (Unit of Work) для контекста учета."""

    invoices: IInvoiceRepository
    payments: IPaymentRepository
    financial_periods: IFinancialPeriodRepository
    rooms: IRoomRepository

    def __init__(self) -> None:
        self.invoices = InMemoryInvoiceRepository()
        self.payments = InMemoryPaymentRepository()
        self.financial_periods = InMemoryFinancialPeriodRepository()
        # Контексту бухгалтерии нужны данные о комнатах для создания счетов,
        # поэтому мы используем реализацию репозитория из контекста бронирования.
        self.rooms = BookingRoomRepository()
        self._committed = True

    async def __aenter__(self) -> IAccountingUnitOfWork:
        self._committed = False
        # Для in-memory UoW настоящий откат потребовал бы глубокого копирования
        # состояния репозиториев здесь. Для этого примера мы просто
        # сбросим их в методе rollback в случае сбоя транзакции.
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_type:
            await self.rollback()
        else:
            await self.commit()

    async def commit(self) -> None:
        """Фиксирует все изменения в рамках единицы работы."""
        # В in-memory реализации просто отмечаем, что изменения сохранены
        self._committed = True

    async def rollback(self) -> None:
        """Откатывает все изменения в рамках единицы работы."""
        # В in-memory реализации сбрасываем репозитории к начальному состоянию
        if not self._committed:
            self.invoices = InMemoryInvoiceRepository()
            self.payments = InMemoryPaymentRepository()
            self.financial_periods = InMemoryFinancialPeriodRepository()
            self.rooms = BookingRoomRepository()


class DummyPaymentGateway(IPaymentGateway):
    """Заглушка платежного шлюза для тестирования."""

    def __init__(self, success_rate: float = 1.0):
        self.success_rate = success_rate
        self.processed_payments: Dict[str, Dict[str, Any]] = {}

    async def process_payment(
        self,
        amount: Money,
        payment_method: str,
        payment_details: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Обрабатывает платеж через внешний платежный шлюз."""
        transaction_id = f"TXN-{uuid4().hex[:8].upper()}"
        success = hash(transaction_id) % 100 < int(self.success_rate * 100)

        result = {
            "transaction_id": transaction_id,
            "status": "completed" if success else "failed",
            "amount": amount.amount,
            "currency": amount.currency,
            "payment_method": payment_method,
            "processed_at": datetime.utcnow().isoformat(),
            "metadata": metadata or {},
        }

        self.processed_payments[transaction_id] = result
        return result

    async def process_refund(
        self,
        payment_id: str,
        amount: Optional[Money] = None,
        reason: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Обрабатывает возврат средств через внешний платежный шлюз."""
        transaction_id = f"RFND-{uuid4().hex[:8].upper()}"

        result = {
            "refund_id": transaction_id,
            "original_payment_id": payment_id,
            "status": "completed",
            "amount": amount.amount if amount else None,
            "currency": amount.currency if amount else None,
            "reason": reason,
            "processed_at": datetime.utcnow().isoformat(),
            "metadata": metadata or {},
        }

        return result

    async def get_payment_status(self, payment_id: str) -> Dict[str, Any]:
        """Проверяет статус платежа во внешнем платежном шлюзе."""
        payment = self.processed_payments.get(payment_id)
        if not payment:
            return {
                "transaction_id": payment_id,
                "status": "not_found",
                "checked_at": datetime.utcnow().isoformat(),
            }

        return {
            "transaction_id": payment_id,
            "status": payment["status"],
            "amount": payment["amount"],
            "currency": payment["currency"],
            "payment_method": payment["payment_method"],
            "processed_at": payment["processed_at"],
            "checked_at": datetime.utcnow().isoformat(),
        }


class ConsoleEmailService(IEmailService):
    """Сервис электронной почты, который выводит сообщения в консоль."""

    async def send_invoice(
        self, to_email: str, invoice: Invoice, context: Dict[str, Any]
    ) -> None:
        """Отправляет счет по email."""
        print("\n--- [Email Service] ---")
        print(f"To: {to_email}")
        print(f"Subject: Счет #{invoice.number} от {invoice.issue_date}")
        print("Body:")
        print("  Уважаемый клиент,")
        print(
            f"  Во вложении ваш счет на сумму {invoice.total.amount} "
            f"{invoice.total.currency}."
        )
        print(f"  Срок оплаты: {invoice.due_date}")
        print(f"  Контекст: {json.dumps(context, indent=2) if context else '{}'}")
        print("--- [End of Email] ---\n")

    async def send_payment_confirmation(
        self, to_email: str, payment: Payment, context: Dict[str, Any]
    ) -> None:
        """Отправляет подтверждение об оплате."""
        print("\n--- [Email Service] ---")
        print(f"To: {to_email}")
        print(f"Subject: Подтверждение оплаты по счету #{payment.invoice_id}")
        print("Body:")
        print("  Уважаемый клиент,")
        print(
            f"  Ваш платеж на сумму {payment.amount.amount} {payment.amount.currency} "
            f"успешно обработан."
        )
        print(f"  ID транзакции: {payment.transaction_id}")
        print(f"  Контекст: {json.dumps(context, indent=2) if context else '{}'}")
        print("--- [End of Email] ---\n")

    async def send_financial_report(
        self,
        to_email: str,
        report_data: bytes,
        report_name: str,
        subject: str,
        message: str = "",
        file_format: str = "pdf",
    ) -> bool:
        """Выводит информацию о финансовом отчете в консоль."""
        print(f"[EMAIL] Отправка финансового отчета '{report_name}' на {to_email}")
        print(f"Тема: {subject}")
        print(f"Формат: {file_format}")
        print(f"Размер данных: {len(report_data)} байт")
        if message:
            print(f"Сообщение: {message}")
        return True


class SimpleFinancialReportGenerator(IFinancialReportGenerator):
    """Простой генератор финансовых отчетов."""

    def __init__(self, uow: IAccountingUnitOfWork):
        self.uow = uow

    async def generate_daily_report(
        self, report_date: date, format: str = "pdf"
    ) -> bytes:
        """Генерирует ежедневный финансовый отчет."""
        # Получаем все счета и платежи за указанную дату
        periods = await self.uow.financial_periods.list_by_date_range(
            start_date=report_date, end_date=report_date
        )

        # В реальной реализации здесь была бы логика генерации отчета
        # в указанном формате (PDF, Excel и т.д.)

        report_data = {
            "report_type": "daily",
            "date": report_date.isoformat(),
            "periods": [
                {
                    "id": str(p.id),
                    "name": p.name,
                    "start_date": p.start_date.isoformat(),
                    "end_date": p.end_date.isoformat(),
                    "status": p.status.value,
                }
                for p in periods
            ],
        }

        return json.dumps(report_data, indent=2, ensure_ascii=False).encode("utf-8")

    async def generate_period_report(
        self, start_date: date, end_date: date, format: str = "pdf"
    ) -> bytes:
        """Генерирует финансовый отчет за указанный период."""
        # Получаем все счета и платежи за указанный период
        periods = await self.uow.financial_periods.list_by_date_range(
            start_date=start_date, end_date=end_date
        )

        # В реальной реализации здесь была бы логика генерации отчета
        # в указанном формате (PDF, Excel и т.д.)

        report_data = {
            "report_type": "period",
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "periods": [
                {
                    "id": str(p.id),
                    "name": p.name,
                    "start_date": p.start_date.isoformat(),
                    "end_date": p.end_date.isoformat(),
                    "status": p.status.value,
                }
                for p in periods
            ],
        }

        return json.dumps(report_data, indent=2, ensure_ascii=False).encode("utf-8")

    async def generate_tax_report(
        self, period: FinancialPeriod, format: str = "pdf"
    ) -> bytes:
        """Генерирует налоговый отчет за указанный период."""
        # В реальной реализации здесь была бы логика генерации налогового отчета
        # в указанном формате (PDF, Excel и т.д.)

        report_data = {
            "report_type": "tax",
            "period": {
                "id": str(period.id),
                "name": period.name,
                "start_date": period.start_date.isoformat(),
                "end_date": period.end_date.isoformat(),
                "status": period.status.value,
            },
            "generated_at": datetime.utcnow().isoformat(),
        }

        return json.dumps(report_data, indent=2, ensure_ascii=False).encode("utf-8")
