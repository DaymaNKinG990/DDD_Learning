"""
Тесты для примеров из модуля "Доменные события (Domain Events)".
Проверяют создание событий, их генерацию в агрегате,
работу диспетчера и вызов обработчиков.
"""

import uuid
from datetime import datetime, timedelta
from typing import cast
from unittest.mock import (  # Используем unittest.mock, если pytest-mock не настроен
    MagicMock,
    call,
)

import pytest

from ddd_course.domain_events_07.domain_events_example_02 import (
    AnalyticsService,  # Импортируем для мокинга
    DomainEvent,
    DomainEventDispatcher,
    EmailService,  # Импортируем для мокинга
    Order,
    OrderCreated,
    OrderIdValueObject,
    OrderPaid,
    OrderStatus,
    UserRegistered,
    handle_order_created_analytics,
    handle_order_created_email,
    handle_order_paid_email_receipt,
    handle_user_registered_analytics,
    handle_user_registered_email,
)


@pytest.fixture
def customer_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def order_items() -> dict:
    return {"Test Product": 1, "Another Product": 2}


@pytest.fixture
def order_total_amount() -> float:
    return 150.75


class TestDomainEventCreation:
    """Тесты создания доменных событий."""

    def test_base_domain_event_creation(self):
        event = DomainEvent()
        assert isinstance(event.event_id, uuid.UUID)
        assert isinstance(event.occurred_on, datetime)
        # Проверка, что время близко к текущему
        assert datetime.utcnow() - event.occurred_on < timedelta(seconds=1)

    def test_user_registered_event_creation(self):
        user_id = uuid.uuid4()
        email = "test@example.com"
        event = UserRegistered(user_id=user_id, email=email)
        assert event.user_id == user_id
        assert event.email == email
        assert isinstance(event, DomainEvent)

    def test_order_created_event_creation(self, customer_id: uuid.UUID):
        order_id_vo = OrderIdValueObject(value=uuid.uuid4())
        amount = 100.0
        event = OrderCreated(
            order_id=order_id_vo, customer_id=customer_id, total_amount=amount
        )
        assert event.order_id == order_id_vo
        assert event.customer_id == customer_id
        assert event.total_amount == amount
        assert isinstance(event, DomainEvent)

    def test_order_paid_event_creation(self):
        order_id_vo = OrderIdValueObject(value=uuid.uuid4())
        payment_ref = "PAY_123"
        event = OrderPaid(order_id=order_id_vo, payment_reference=payment_ref)
        assert event.order_id == order_id_vo
        assert event.payment_reference == payment_ref
        assert isinstance(event, DomainEvent)


class TestOrderAggregateEvents:
    """Тесты генерации событий агрегатом Order."""

    def test_order_creation_generates_order_created_event(
        self, customer_id: uuid.UUID, order_items: dict, order_total_amount: float
    ):
        order = Order.create(customer_id, order_items, order_total_amount)
        events = order.pull_domain_events()

        assert len(events) == 1
        event = events[0]
        assert isinstance(event, OrderCreated)
        assert event.order_id == order.id
        assert event.customer_id == customer_id
        assert event.total_amount == order_total_amount
        assert (
            len(order.pull_domain_events()) == 0
        ), "Events should be cleared after pulling"

    def test_order_payment_generates_order_paid_event(
        self, customer_id: uuid.UUID, order_items: dict, order_total_amount: float
    ):
        order = Order.create(customer_id, order_items, order_total_amount)
        order.pull_domain_events()  # Clear initial event

        payment_ref = "PAY_XYZ789"
        order.pay(payment_ref)
        events = order.pull_domain_events()

        assert len(events) == 1
        event = events[0]
        assert isinstance(event, OrderPaid)
        assert event.order_id == order.id
        assert event.payment_reference == payment_ref
        assert order.status == OrderStatus.PAID
        assert len(order.pull_domain_events()) == 0

    def test_pay_already_paid_order_raises_error(
        self, customer_id: uuid.UUID, order_items: dict, order_total_amount: float
    ):
        order = Order.create(customer_id, order_items, order_total_amount)
        order.pay("REF1")
        order.pull_domain_events()  # Clear events

        with pytest.raises(ValueError, match="Заказ уже оплачен."):
            order.pay("REF2")
        assert len(order.pull_domain_events()) == 0, "No new events on error"


class TestDomainEventDispatcher:
    """Тесты для DomainEventDispatcher."""

    @pytest.fixture
    def dispatcher(self) -> DomainEventDispatcher:
        return DomainEventDispatcher()

    @pytest.fixture
    def mock_handler_one(self) -> MagicMock:
        return MagicMock()

    @pytest.fixture
    def mock_handler_two(self) -> MagicMock:
        return MagicMock()

    def test_register_and_dispatch_single_handler(
        self, dispatcher: DomainEventDispatcher, mock_handler_one: MagicMock
    ):
        event = UserRegistered(user_id=uuid.uuid4(), email="test@example.com")
        dispatcher.register(UserRegistered, mock_handler_one)
        dispatcher.dispatch(event)
        mock_handler_one.assert_called_once_with(event)

    def test_dispatch_multiple_handlers_for_same_event(
        self,
        dispatcher: DomainEventDispatcher,
        mock_handler_one: MagicMock,
        mock_handler_two: MagicMock,
    ):
        event = UserRegistered(user_id=uuid.uuid4(), email="test@example.com")
        dispatcher.register(UserRegistered, mock_handler_one)
        dispatcher.register(UserRegistered, mock_handler_two)
        dispatcher.dispatch(event)
        mock_handler_one.assert_called_once_with(event)
        mock_handler_two.assert_called_once_with(event)

    def test_dispatch_no_handler_registered(
        self, dispatcher: DomainEventDispatcher, mock_handler_one: MagicMock
    ):
        event = OrderCreated(
            order_id=OrderIdValueObject(uuid.uuid4()),
            customer_id=uuid.uuid4(),
            total_amount=10.0,
        )
        # mock_handler_one is registered for UserRegistered, not OrderCreated
        dispatcher.register(UserRegistered, mock_handler_one)
        dispatcher.dispatch(event)  # Should not call mock_handler_one
        mock_handler_one.assert_not_called()

    def test_dispatch_different_event_types(
        self,
        dispatcher: DomainEventDispatcher,
        mock_handler_one: MagicMock,
        mock_handler_two: MagicMock,
    ):
        user_event = UserRegistered(user_id=uuid.uuid4(), email="user@example.com")
        order_event = OrderCreated(
            order_id=OrderIdValueObject(uuid.uuid4()),
            customer_id=uuid.uuid4(),
            total_amount=20.0,
        )

        dispatcher.register(UserRegistered, mock_handler_one)
        dispatcher.register(OrderCreated, mock_handler_two)

        dispatcher.dispatch(user_event)
        mock_handler_one.assert_called_once_with(user_event)
        mock_handler_two.assert_not_called()

        mock_handler_one.reset_mock()
        dispatcher.dispatch(order_event)
        mock_handler_one.assert_not_called()
        mock_handler_two.assert_called_once_with(order_event)

    def test_dispatch_batch(
        self,
        dispatcher: DomainEventDispatcher,
        mock_handler_one: MagicMock,
        mock_handler_two: MagicMock,
    ):
        user_event = UserRegistered(user_id=uuid.uuid4(), email="user1@example.com")
        order_event = OrderCreated(
            order_id=OrderIdValueObject(uuid.uuid4()),
            customer_id=uuid.uuid4(),
            total_amount=30.0,
        )
        another_user_event = UserRegistered(
            user_id=uuid.uuid4(), email="user2@example.com"
        )

        dispatcher.register(UserRegistered, mock_handler_one)
        dispatcher.register(OrderCreated, mock_handler_two)

        events_batch = [user_event, order_event, another_user_event]
        dispatcher.dispatch_batch(events_batch)

        assert mock_handler_one.call_count == 2
        mock_handler_one.assert_has_calls([call(user_event), call(another_user_event)])
        mock_handler_two.assert_called_once_with(order_event)

    def test_handler_exception_does_not_stop_other_handlers(
        self, dispatcher: DomainEventDispatcher, mock_handler_two: MagicMock
    ):
        failing_handler = MagicMock(side_effect=RuntimeError("Handler failed!"))
        event = UserRegistered(user_id=uuid.uuid4(), email="test@example.com")

        dispatcher.register(UserRegistered, failing_handler)
        dispatcher.register(UserRegistered, mock_handler_two)

        # pytest.raises(RuntimeError) # Это не то, что мы хотим здесь проверить.
        # Instead, we check that the second handler was still called.
        # The example dispatcher prints errors but continues.
        dispatcher.dispatch(event)

        failing_handler.assert_called_once_with(event)
        mock_handler_two.assert_called_once_with(
            event
        )  # Crucial: this should still be called


class TestEventHandlersIntegration:
    """Тесты интеграции обработчиков событий с моками сервисов."""

    @pytest.fixture
    def dispatcher(self) -> DomainEventDispatcher:
        # Каждый тест получает свой экземпляр диспетчера
        return DomainEventDispatcher()

    @pytest.fixture(autouse=True)
    def mock_email_service(self, mocker) -> MagicMock:
        # Мокаем глобальный экземпляр EmailService
        mock = mocker.patch(
            "ddd_course.domain_events_07.domain_events_example_02.email_service",
            spec_set=EmailService,
        )
        return cast(MagicMock, mock)

    @pytest.fixture(autouse=True)
    def mock_analytics_service(self, mocker) -> MagicMock:
        # Мокаем глобальный экземпляр AnalyticsService
        mock = mocker.patch(
            "ddd_course.domain_events_07.domain_events_example_02.analytics_service",
            spec_set=AnalyticsService,
        )
        return cast(MagicMock, mock)

    def test_handle_user_registered_event(
        self,
        dispatcher: DomainEventDispatcher,
        mock_email_service: MagicMock,
        mock_analytics_service: MagicMock,
    ):
        dispatcher.register(UserRegistered, handle_user_registered_email)
        dispatcher.register(UserRegistered, handle_user_registered_analytics)

        user_id = uuid.uuid4()
        email = "new.user@domain.com"
        event = UserRegistered(user_id=user_id, email=email)
        dispatcher.dispatch(event)

        mock_email_service.send_welcome_email.assert_called_once_with(email, user_id)
        mock_analytics_service.track_user_registration.assert_called_once_with(
            user_id, event.occurred_on
        )

    def test_handle_order_created_event(
        self,
        dispatcher: DomainEventDispatcher,
        mock_email_service: MagicMock,
        mock_analytics_service: MagicMock,
        customer_id: uuid.UUID,
    ):
        dispatcher.register(OrderCreated, handle_order_created_email)
        dispatcher.register(OrderCreated, handle_order_created_analytics)

        order_id_vo = OrderIdValueObject(value=uuid.uuid4())
        amount = 250.0
        event = OrderCreated(
            order_id=order_id_vo, customer_id=customer_id, total_amount=amount
        )
        dispatcher.dispatch(event)

        mock_email_service.send_order_confirmation_email.assert_called_once_with(
            customer_id, order_id_vo, amount
        )
        mock_analytics_service.track_order_creation.assert_called_once_with(
            order_id_vo, amount, event.occurred_on
        )

    def test_handle_order_paid_event(
        self,
        dispatcher: DomainEventDispatcher,
        mock_email_service: MagicMock,
        customer_id: uuid.UUID,
    ):
        # Мокаем uuid.uuid4, используемый как placeholder в обработчике
        # чтобы сделать утверждение предсказуемым.
        # Это немного хрупко, так как зависит от детали реализации обработчика.
        # Лучше было бы, если бы обработчик получал customer_id более надежным способом.
        # mocker.patch(
        #     'ddd_course.domain_events_07.domain_events_example_02.uuid.uuid4',
        #     return_value=customer_id
        # )
        # Вместо сложного мокинга uuid.uuid4, просто проверим вызов метода
        # с любым UUID для customer_id, так как он является заглушкой в обработчике.

        dispatcher.register(OrderPaid, handle_order_paid_email_receipt)

        order_id_vo = OrderIdValueObject(value=uuid.uuid4())
        payment_ref = "PAY_REF_FOR_TEST"
        event = OrderPaid(order_id=order_id_vo, payment_reference=payment_ref)
        dispatcher.dispatch(event)

        # Проверяем, что send_payment_receipt_email был вызван.
        # Мы не можем точно утверждать customer_id, т.к. он генерируется как заглушка.
        # Поэтому используем unittest.mock.ANY или проверяем только другие аргументы.
        assert mock_email_service.send_payment_receipt_email.call_count == 1
        call_args = mock_email_service.send_payment_receipt_email.call_args
        assert (
            call_args[0][0] is not None
        )  # customer_id (placeholder) should not be None
        assert isinstance(call_args[0][0], uuid.UUID)
        assert call_args[0][1] == order_id_vo
        assert call_args[0][2] == payment_ref
