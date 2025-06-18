"""
Интерфейсы (порты) контекста учета.

Определяет контракты для репозиториев и сервисов,
которые должны быть реализованы во внешних слоях.
"""
from abc import ABC, abstractmethod
from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional, Dict, Any, Set, Tuple
from uuid import UUID

from pydantic import BaseModel

from shared_kernel import EntityId, Money
from .domain import (
    Invoice, 
    InvoiceStatus, 
    Payment, 
    PaymentStatus, 
    FinancialPeriod,
    FinancialPeriodStatus,
    InvoiceItem
)


class IInvoiceRepository(ABC):
    """Интерфейс репозитория счетов."""
    
    @abstractmethod
    async def get_by_id(self, invoice_id: EntityId) -> Optional[Invoice]:
        """Возвращает счет по идентификатору."""
        pass
    
    @abstractmethod
    async def get_by_number(self, number: str) -> Optional[Invoice]:
        """Возвращает счет по номеру."""
        pass
    
    @abstractmethod
    async def list_by_guest(
        self, 
        guest_id: EntityId, 
        status: Optional[InvoiceStatus] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Invoice]:
        """Возвращает список счетов гостя."""
        pass
    
    @abstractmethod
    async def list_by_booking(
        self, 
        booking_id: EntityId, 
        status: Optional[InvoiceStatus] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Invoice]:
        """Возвращает список счетов по бронированию."""
        pass
    
    @abstractmethod
    async def list_by_status(
        self, 
        status: InvoiceStatus,
        limit: int = 100,
        offset: int = 0
    ) -> List[Invoice]:
        """Возвращает список счетов по статусу."""
        pass
    
    @abstractmethod
    async def list_overdue(
        self, 
        as_of_date: Optional[date] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Invoice]:
        """Возвращает список просроченных счетов."""
        pass
    
    @abstractmethod
    async def save(self, invoice: Invoice) -> None:
        """Сохраняет счет."""
        pass
    
    @abstractmethod
    async def delete(self, invoice_id: EntityId) -> bool:
        """Удаляет счет по идентификатору."""
        pass


class IPaymentRepository(ABC):
    """Интерфейс репозитория платежей."""
    
    @abstractmethod
    async def get_by_id(self, payment_id: EntityId) -> Optional[Payment]:
        """Возвращает платеж по идентификатору."""
        pass
    
    @abstractmethod
    async def list_by_invoice(
        self, 
        invoice_id: EntityId, 
        status: Optional[PaymentStatus] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Payment]:
        """Возвращает список платежей по счету."""
        pass
    
    @abstractmethod
    async def list_by_guest(
        self, 
        guest_id: EntityId, 
        status: Optional[PaymentStatus] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Payment]:
        """Возвращает список платежей гостя."""
        pass
    
    @abstractmethod
    async def list_by_status(
        self, 
        status: PaymentStatus,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Payment]:
        """Возвращает список платежей по статусу."""
        pass
    
    @abstractmethod
    async def save(self, payment: Payment) -> None:
        """Сохраняет платеж."""
        pass


class IFinancialPeriodRepository(ABC):
    """Интерфейс репозитория финансовых периодов."""
    
    @abstractmethod
    async def get_by_id(self, period_id: EntityId) -> Optional[FinancialPeriod]:
        """Возвращает финансовый период по идентификатору."""
        pass
    
    @abstractmethod
    async def get_by_date(
        self, 
        date: date
    ) -> Optional[FinancialPeriod]:
        """Возвращает финансовый период, в который входит указанная дата."""
        pass
    
    @abstractmethod
    async def list_by_status(
        self, 
        status: FinancialPeriodStatus,
        limit: int = 100,
        offset: int = 0
    ) -> List[FinancialPeriod]:
        """Возвращает список финансовых периодов по статусу."""
        pass
    
    @abstractmethod
    async def list_by_date_range(
        self, 
        start_date: date, 
        end_date: date,
        limit: int = 100,
        offset: int = 0
    ) -> List[FinancialPeriod]:
        """Возвращает список финансовых периодов в указанном диапазоне дат."""
        pass
    
    @abstractmethod
    async def get_current_period(self) -> Optional[FinancialPeriod]:
        """Возвращает текущий открытый финансовый период."""
        pass
    
    @abstractmethod
    async def save(self, period: FinancialPeriod) -> None:
        """Сохраняет финансовый период."""
        pass


class IAccountingUnitOfWork(ABC):
    """Интерфейс единицы работы (Unit of Work) для контекста учета."""
    
    invoices: IInvoiceRepository
    payments: IPaymentRepository
    financial_periods: IFinancialPeriodRepository
    
    @abstractmethod
    async def commit(self) -> None:
        """Фиксирует все изменения в рамках единицы работы."""
        pass
    
    @abstractmethod
    async def rollback(self) -> None:
        """Откатывает все изменения в рамках единицы работы."""
        pass


class IPaymentGateway(ABC):
    """Интерфейс платежного шлюза."""
    
    @abstractmethod
    async def process_payment(
        self,
        amount: Money,
        payment_method: str,
        payment_details: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Обрабатывает платеж через внешний платежный шлюз."""
        pass
    
    @abstractmethod
    async def process_refund(
        self,
        payment_id: str,
        amount: Optional[Money] = None,
        reason: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Обрабатывает возврат средств через внешний платежный шлюз."""
        pass
    
    @abstractmethod
    async def get_payment_status(
        self,
        payment_id: str
    ) -> Dict[str, Any]:
        """Проверяет статус платежа во внешнем платежном шлюзе."""
        pass


class IFinancialReportGenerator(ABC):
    """Интерфейс генератора финансовых отчетов."""
    
    @abstractmethod
    async def generate_daily_report(
        self,
        report_date: date,
        format: str = "pdf"
    ) -> bytes:
        """Генерирует ежедневный финансовый отчет."""
        pass
    
    @abstractmethod
    async def generate_period_report(
        self,
        start_date: date,
        end_date: date,
        format: str = "pdf"
    ) -> bytes:
        """Генерирует финансовый отчет за указанный период."""
        pass
    
    @abstractmethod
    async def generate_tax_report(
        self,
        period: FinancialPeriod,
        format: str = "pdf"
    ) -> bytes:
        """Генерирует налоговый отчет за указанный период."""
        pass


class IEmailService(ABC):
    """Интерфейс сервиса электронной почты."""
    
    @abstractmethod
    async def send_invoice(
        self,
        to_email: str,
        invoice: Invoice,
        template_name: str = "invoice.html",
        context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Отправляет счет по электронной почте."""
        pass
    
    @abstractmethod
    async def send_payment_confirmation(
        self,
        to_email: str,
        payment: Payment,
        template_name: str = "payment_confirmation.html",
        context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Отправляет подтверждение платежа по электронной почте."""
        pass
    
    @abstractmethod
    async def send_financial_report(
        self,
        to_email: str,
        report_data: bytes,
        report_name: str,
        subject: str,
        message: str = "",
        format: str = "pdf"
    ) -> bool:
        """Отправляет финансовый отчет по электронной почте."""
        pass


class IAccountingService(ABC):
    """Интерфейс сервиса учета."""
    
    @abstractmethod
    async def create_invoice(
        self,
        guest_id: EntityId,
        items: List[InvoiceItem],
        due_date: date,
        booking_id: Optional[EntityId] = None,
        notes: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Invoice:
        """Создает новый счет."""
        pass
    
    @abstractmethod
    async def issue_invoice(self, invoice_id: EntityId) -> Invoice:
        """Выставляет счет (переводит в статус ISSUED)."""
        pass
    
    @abstractmethod
    async def cancel_invoice(
        self, 
        invoice_id: EntityId, 
        reason: Optional[str] = None
    ) -> Invoice:
        """Аннулирует счет."""
        pass
    
    @abstractmethod
    async def record_payment(
        self,
        invoice_id: EntityId,
        amount: Money,
        payment_method: str,
        transaction_id: Optional[str] = None,
        notes: Optional[str] = None,
        process_online: bool = False
    ) -> Payment:
        """Регистрирует платеж по счету."""
        pass
    
    @abstractmethod
    async def process_payment(
        self,
        payment_id: EntityId
    ) -> Payment:
        """Обрабатывает ожидающий платеж."""
        pass
    
    @abstractmethod
    async def issue_refund(
        self,
        payment_id: EntityId,
        amount: Optional[Money] = None,
        reason: Optional[str] = None,
        process_online: bool = False
    ) -> Payment:
        """Выполняет возврат средств."""
        pass
    
    @abstractmethod
    async def close_financial_period(
        self,
        period_id: EntityId,
        closed_by: EntityId
    ) -> FinancialPeriod:
        """Закрывает финансовый период."""
        pass
    
    @abstractmethod
    async def generate_financial_report(
        self,
        start_date: date,
        end_date: date,
        format: str = "pdf"
    ) -> bytes:
        """Генерирует финансовый отчет за указанный период."""
        pass
