"""
Тесты интеграции контекстов Booking и Accounting.
"""

from datetime import date, timedelta
from decimal import Decimal

import pytest
from accounting.application import AccountingApplicationService
from accounting.domain import (
    InvoiceStatus,
    PaymentMethod,
    PaymentStatus,
)
from accounting.infrastructure import (
    AccountingUnitOfWork,
    ConsoleEmailService,
    DummyPaymentGateway,
    SimpleFinancialReportGenerator,
)
from booking.application import BookingApplicationService
from booking.domain import BookingStatus, Guest, Room, RoomStatus, RoomType
from booking.infrastructure import (
    BookingUnitOfWork,
)
from shared_kernel import Money


class TestBookingAccountingIntegration:
    """Тесты интеграции контекстов Booking и Accounting."""

    @pytest.fixture
    async def booking_service(self):
        """Создает экземпляр сервиса бронирования для тестирования."""
        uow = BookingUnitOfWork()

        # Добавляем тестовые данные
        room = Room(
            number="101",
            type=RoomType.STANDARD,
            price_per_night=Money(amount=Decimal("2500.00")),
            capacity=2,
            status=RoomStatus.AVAILABLE,
        )
        await uow.rooms.save(room)

        guest = Guest(
            first_name="Иван",
            last_name="Иванов",
            email="ivan@example.com",
            phone="+79001234567",
        )
        await uow.guests.save(guest)

        return BookingApplicationService(uow)

    @pytest.fixture
    async def accounting_service(self):
        """Создает экземпляр сервиса учета для тестирования."""
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

    async def test_booking_creates_invoice(self, booking_service, accounting_service):
        """
        Тестирует создание счета при бронировании номера.

        Проверяет, что при успешном бронировании номера
        автоматически создается счет на оплату.
        """
        # Подготовка - получаем тестовые данные
        rooms = await booking_service.uow.rooms.list_available(
            start_date=date.today(), end_date=date.today() + timedelta(days=3)
        )
        assert len(rooms) > 0, "Нет доступных номеров для тестирования"

        room = rooms[0]
        guests = await booking_service.uow.guests.list()
        assert len(guests) > 0, "Нет гостей для тестирования"

        guest = guests[0]
        check_in = date.today()
        check_out = date.today() + timedelta(days=3)

        # Действие - создаем бронирование
        booking = await booking_service.create_booking(
            room_id=room.id,
            guest_id=guest.id,
            check_in=check_in,
            check_out=check_out,
            guest_count=1,
            special_requests="Тестовое бронирование",
        )

        # Проверяем, что бронирование создано
        assert booking is not None
        assert booking.status == BookingStatus.CONFIRMED

        # Проверяем, что создан счет на оплату
        invoices = await accounting_service.uow.invoices.list_by_booking(
            booking_id=booking.id
        )

        assert len(invoices) > 0, "Счет на оплату не создан"
        invoice = invoices[0]

        # Проверяем детали счета
        assert invoice.guest_id == guest.id
        assert invoice.booking_id == booking.id
        assert invoice.status == InvoiceStatus.ISSUED

        # Проверяем позиции в счете
        assert len(invoice.items) > 0

        # Ожидаемая сумма: цена за ночь * количество ночей
        expected_amount = room.price_per_night * (check_out - check_in).days
        assert invoice.total.amount == expected_amount.amount

    async def test_payment_confirms_booking(self, booking_service, accounting_service):
        """
        Тестирует подтверждение бронирования при оплате счета.

        Проверяет, что при успешной оплате счета
        статус бронирования меняется на "Оплачено".
        """
        # Подготовка - создаем тестовое бронирование
        rooms = await booking_service.uow.rooms.list_available(
            start_date=date.today(), end_date=date.today() + timedelta(days=2)
        )
        room = rooms[0]

        guests = await booking_service.uow.guests.list()
        guest = guests[0]

        booking = await booking_service.create_booking(
            room_id=room.id,
            guest_id=guest.id,
            check_in=date.today(),
            check_out=date.today() + timedelta(days=2),
            guest_count=1,
        )

        # Получаем счет на оплату
        invoices = await accounting_service.uow.invoices.list_by_booking(booking.id)
        invoice = invoices[0]

        # Действие - оплачиваем счет
        payment = await accounting_service.record_payment(
            invoice_id=invoice.id,
            amount=invoice.total,
            payment_method=PaymentMethod.CREDIT_CARD.value,
            notes="Оплата бронирования",
            process_online=True,
        )

        # Проверяем, что платеж успешно обработан
        assert payment.status == PaymentStatus.COMPLETED

        # Проверяем, что статус счета обновлен
        updated_invoice = await accounting_service.uow.invoices.get_by_id(invoice.id)
        assert updated_invoice.status == InvoiceStatus.PAID

        # Проверяем, что статус бронирования обновлен
        updated_booking = await booking_service.uow.bookings.get_by_id(booking.id)
        assert updated_booking.status == BookingStatus.PAID

    async def test_booking_cancellation_creates_refund(
        self, booking_service, accounting_service
    ):
        """
        Тестирует создание возврата при отмене бронирования.

        Проверяет, что при отмене оплаченного бронирования
        создается возврат средств.
        """
        # Подготовка - создаем и оплачиваем бронирование
        rooms = await booking_service.uow.rooms.list_available(
            start_date=date.today(), end_date=date.today() + timedelta(days=3)
        )
        room = rooms[0]

        guests = await booking_service.uow.guests.list()
        guest = guests[0]

        booking = await booking_service.create_booking(
            room_id=room.id,
            guest_id=guest.id,
            check_in=date.today() + timedelta(days=1),
            check_out=date.today() + timedelta(days=4),
            guest_count=1,
        )

        # Оплачиваем бронирование
        invoices = await accounting_service.uow.invoices.list_by_booking(booking.id)
        invoice = invoices[0]

        payment = await accounting_service.record_payment(
            invoice_id=invoice.id,
            amount=invoice.total,
            payment_method=PaymentMethod.CREDIT_CARD.value,
            process_online=True,
        )

        # Действие - отменяем бронирование
        cancelled_booking = await booking_service.cancel_booking(
            booking_id=booking.id, reason="Изменение планов"
        )

        # Проверяем, что бронирование отменено
        assert cancelled_booking.status == BookingStatus.CANCELLED

        # Проверяем, что создан возврат средств
        refunds = await accounting_service.uow.payments.list_by_invoice(
            invoice_id=invoice.id, status=PaymentStatus.REFUNDED
        )

        assert len(refunds) > 0, "Возврат средств не создан"
        refund = refunds[0]

        # Проверяем детали возврата
        assert refund.amount.amount > 0
        assert refund.metadata.get("original_payment_id") == str(payment.id)
        assert "отмена бронирования" in refund.notes.lower()

    async def test_early_checkout_creates_adjustment(
        self, booking_service, accounting_service
    ):
        """
        Тестирует создание корректировки при досрочном выезде.

        Проверяет, что при досрочном выезде гостя
        создается корректировка счета.
        """
        # Подготовка - создаем и оплачиваем бронирование
        rooms = await booking_service.uow.rooms.list_available(
            start_date=date.today(), end_date=date.today() + timedelta(days=5)
        )
        room = rooms[0]

        guests = await booking_service.uow.guests.list()
        guest = guests[0]

        check_in = date.today()
        original_check_out = date.today() + timedelta(days=5)
        actual_check_out = date.today() + timedelta(days=3)  # Досрочный выезд

        booking = await booking_service.create_booking(
            room_id=room.id,
            guest_id=guest.id,
            check_in=check_in,
            check_out=original_check_out,
            guest_count=1,
        )

        # Оплачиваем бронирование
        invoices = await accounting_service.uow.invoices.list_by_booking(booking.id)
        invoice = invoices[0]

        await accounting_service.record_payment(
            invoice_id=invoice.id,
            amount=invoice.total,
            payment_method=PaymentMethod.CREDIT_CARD.value,
            process_online=True,
        )

        # Действие - регистрируем досрочный выезд
        await booking_service.check_out_guest(
            booking_id=booking.id, actual_check_out=actual_check_out
        )

        # Проверяем, что создана корректировка счета
        updated_invoice = await accounting_service.uow.invoices.get_by_id(invoice.id)

        # Ищем позицию с корректировкой
        adjustment_items = [
            item
            for item in updated_invoice.items
            if "корректировка" in item.description.lower()
        ]

        assert len(adjustment_items) > 0, "Корректировка не создана"
        adjustment = adjustment_items[0]

        # Проверяем, что сумма корректировки отрицательная (возврат)
        expected_nights = (original_check_out - actual_check_out).days
        expected_refund = room.price_per_night * expected_nights

        assert adjustment.unit_price.amount == -expected_refund.amount
        assert "досрочный выезд" in adjustment.description.lower()

        # Проверяем, что общая сумма счета уменьшилась
        assert updated_invoice.total.amount < invoice.total.amount
        assert updated_invoice.total.amount == (invoice.total - expected_refund).amount


class TestEventDrivenIntegration:
    """Тесты событийной интеграции между контекстами."""

    async def test_booking_created_event_triggers_invoice_creation(self):
        """
        Тестирует создание счета при получении события о создании бронирования.
        """
        # В реальном приложении здесь была бы подписка на события
        # и проверка, что обработчик создает счет
        pass

    async def test_payment_received_event_confirms_booking(self):
        """
        Тестирует подтверждение бронирования при получении события об оплате.
        """
        # В реальном приложении здесь была бы подписка на события
        # и проверка, что обработчик обновляет статус бронирования
        pass

    async def test_booking_cancelled_event_triggers_refund(self):
        """
        Тестирует создание возврата при получении события об отмене бронирования.
        """
        # В реальном приложении здесь была бы подписка на события
        # и проверка, что обработчик создает возврат
        pass
