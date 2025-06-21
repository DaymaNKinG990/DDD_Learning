from functools import partial

from accounting.application import create_accounting_service
from accounting.event_handlers import on_booking_created
from booking.domain import BookingCreated
from booking.infrastructure import BookingUnitOfWork


def bootstrap_app():
    """Создает и настраивает все компоненты приложения."""
    # 1. Создаем Unit of Work для контекста бронирования
    booking_uow = BookingUnitOfWork()

    # 2. Создаем сервисы, передавая им зависимости
    accounting_service = create_accounting_service(
        # Передаем репозиторий номеров из одного контекста в другой
        room_repo=booking_uow.rooms
    )

    # 3. Подписываем обработчики на события
    # Создаем partial, чтобы передать сервис в обработчик
    handler = partial(on_booking_created, service=accounting_service)
    booking_uow.event_bus.subscribe(BookingCreated, handler)

    # Возвращаем настроенные компоненты
    return {
        "booking_uow": booking_uow,
        "accounting_service": accounting_service,
    }
