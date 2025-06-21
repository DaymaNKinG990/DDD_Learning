from booking.domain import BookingCreated

from .interfaces import IAccountingService


async def on_booking_created(
    event: BookingCreated, service: "IAccountingService"
) -> None:
    """Обработчик события создания бронирования."""
    await service.create_invoice_for_booking(event)
