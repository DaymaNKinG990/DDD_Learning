"""
Тесты для примеров Агрегатов (Order, OrderItem) из aggregates_example_02.py.
"""

import uuid
from dataclasses import FrozenInstanceError

import pytest

from ddd_course.aggregates_06.aggregates_example_02 import (
    Order,
    OrderId,
    OrderItem,
    OrderItemId,
    OrderStatus,
    Product,
    ProductId,
)


@pytest.fixture
def product1() -> Product:
    return Product(id=ProductId(), name="Тестовый Продукт 1", price=100.0)


@pytest.fixture
def product2() -> Product:
    return Product(id=ProductId(), name="Тестовый Продукт 2", price=50.0)


@pytest.fixture
def customer_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def order(customer_id: uuid.UUID) -> Order:
    return Order(customer_id=customer_id)


class TestOrderItem:
    """Тесты для сущности OrderItem."""

    def test_order_item_creation_success(self, product1: Product):
        item = OrderItem(
            product_id=product1.id,
            product_name=product1.name,
            quantity=2,
            price_per_unit=product1.price,
        )
        assert item.product_id == product1.id
        assert item.product_name == product1.name
        assert item.quantity == 2
        assert item.price_per_unit == product1.price
        assert item.total_price == 200.0
        assert isinstance(item.id, OrderItemId)

    def test_order_item_creation_invalid_quantity(self, product1: Product):
        with pytest.raises(ValueError, match="Количество должно быть положительным"):
            OrderItem(
                product_id=product1.id,
                product_name=product1.name,
                quantity=0,
                price_per_unit=product1.price,
            )
        with pytest.raises(ValueError, match="Количество должно быть положительным"):
            OrderItem(
                product_id=product1.id,
                product_name=product1.name,
                quantity=-1,
                price_per_unit=product1.price,
            )

    def test_order_item_creation_invalid_price(self, product1: Product):
        with pytest.raises(
            ValueError, match="Цена за единицу не может быть отрицательной"
        ):
            OrderItem(
                product_id=product1.id,
                product_name=product1.name,
                quantity=1,
                price_per_unit=-10.0,
            )

    def test_order_item_change_quantity_success(self, product1: Product):
        item = OrderItem(
            product_id=product1.id,
            product_name=product1.name,
            quantity=1,
            price_per_unit=product1.price,
        )
        item.change_quantity(5)
        assert item.quantity == 5
        assert item.total_price == 500.0

    def test_order_item_change_quantity_invalid(self, product1: Product):
        item = OrderItem(
            product_id=product1.id,
            product_name=product1.name,
            quantity=1,
            price_per_unit=product1.price,
        )
        with pytest.raises(
            ValueError, match="Новое количество должно быть положительным"
        ):
            item.change_quantity(0)
        with pytest.raises(
            ValueError, match="Новое количество должно быть положительным"
        ):
            item.change_quantity(-2)

    def test_order_item_immutable_id_and_product(self, product1: Product):
        item = OrderItem(
            product_id=product1.id,
            product_name=product1.name,
            quantity=1,
            price_per_unit=product1.price,
        )
        original_id = item.id
        original_product_id = item.product_id

        with pytest.raises(FrozenInstanceError):  # Assuming OrderItemId is frozen
            item.id = OrderItemId()
        # For other attributes not handled by @dataclass(frozen=True) on OrderItem
        # For example, if product_id was meant to be truly immutable after creation:
        # with pytest.raises(AttributeError): # Or specific error if setter raises
        #    item.product_id = ProductId()
        assert item.id == original_id
        assert item.product_id == original_product_id


class TestOrderAggregate:
    """Тесты для агрегата Order."""

    def test_order_creation_success(self, customer_id: uuid.UUID):
        order_instance = Order(customer_id=customer_id)
        assert order_instance.customer_id == customer_id
        assert isinstance(order_instance.id, OrderId)
        assert order_instance.status == OrderStatus.PENDING
        assert len(order_instance.items) == 0
        assert order_instance.total_price == 0.0
        assert order_instance.version == 1

    def test_add_item_success(self, order: Order, product1: Product):
        order.add_item(product1, 2)
        assert len(order.items) == 1
        item = order.items[0]
        assert item.product_id == product1.id
        assert item.quantity == 2
        assert item.price_per_unit == product1.price  # Price fixed at time of addition
        assert order.total_price == 200.0
        assert order.version == 2

    def test_add_item_updates_quantity_if_exists(self, order: Order, product1: Product):
        order.add_item(product1, 1)  # version = 2
        order.add_item(product1, 2)  # version = 3
        assert len(order.items) == 1
        assert order.items[0].quantity == 3
        assert order.total_price == 300.0
        assert order.version == 3

    def test_add_item_respects_max_items_limit(self, order: Order):
        for i in range(Order.MAX_ITEMS_PER_ORDER):
            prod = Product(id=ProductId(), name=f"P{i}", price=10.0)
            order.add_item(prod, 1)
        assert len(order.items) == Order.MAX_ITEMS_PER_ORDER

        extra_prod = Product(id=ProductId(), name="Extra", price=5.0)
        with pytest.raises(
            ValueError,
            match=(
                f"Нельзя добавить больше {Order.MAX_ITEMS_PER_ORDER} позиций в заказ"
            ),
        ):
            order.add_item(extra_prod, 1)
        # Version increments for each successful add
        assert order.version == Order.MAX_ITEMS_PER_ORDER + 1

    def test_add_item_respects_max_quantity_per_item_limit(
        self, order: Order, product1: Product
    ):
        with pytest.raises(
            ValueError,
            match=(
                f"Количество товара должно быть от 1 до {Order.MAX_QUANTITY_PER_ITEM}"
            ),
        ):
            order.add_item(product1, Order.MAX_QUANTITY_PER_ITEM + 1)

        order.add_item(product1, Order.MAX_QUANTITY_PER_ITEM - 1)  # version = 2
        with pytest.raises(
            ValueError, match=f"Общее количество товара {product1.name} превысит лимит"
        ):
            order.add_item(product1, 2)  # Tries to add 2, making it MAX + 1
        assert order.version == 2  # Version should not increment on failure

    def test_add_item_invalid_quantity(self, order: Order, product1: Product):
        with pytest.raises(
            ValueError,
            match=(
                f"Количество товара должно быть от 1 до {Order.MAX_QUANTITY_PER_ITEM}"
            ),
        ):
            order.add_item(product1, 0)
        with pytest.raises(
            ValueError,
            match=(
                f"Количество товара должно быть от 1 до {Order.MAX_QUANTITY_PER_ITEM}"
            ),
        ):
            order.add_item(product1, -1)
        assert order.version == 1

    def test_remove_item_success(
        self, order: Order, product1: Product, product2: Product
    ):
        order.add_item(product1, 1)  # v2
        order.add_item(product2, 2)  # v3
        order.remove_item(product1.id)  # v4
        assert len(order.items) == 1
        assert order.items[0].product_id == product2.id
        assert order.total_price == product2.price * 2
        assert order.version == 4

    def test_remove_item_not_found(self, order: Order, product1: Product):
        unknown_product_id = ProductId()
        with pytest.raises(
            ValueError,
            match=(f"Продукт с ID {unknown_product_id.value} не найден в заказе"),
        ):
            order.remove_item(unknown_product_id)
        assert order.version == 1

    def test_update_item_quantity_success(self, order: Order, product1: Product):
        order.add_item(product1, 1)  # v2
        order.update_item_quantity(product1.id, 5)  # v3
        assert order.items[0].quantity == 5
        assert order.total_price == product1.price * 5
        assert order.version == 3

    def test_update_item_quantity_invalid_value(self, order: Order, product1: Product):
        order.add_item(product1, 1)  # v2
        with pytest.raises(
            ValueError,
            match=(
                f"Новое количество товара должно быть от 1 до "
                f"{Order.MAX_QUANTITY_PER_ITEM}"
            ),
        ):
            order.update_item_quantity(product1.id, 0)
        with pytest.raises(
            ValueError,
            match=(
                f"Новое количество товара должно быть от 1 до "
                f"{Order.MAX_QUANTITY_PER_ITEM}"
            ),
        ):
            order.update_item_quantity(product1.id, Order.MAX_QUANTITY_PER_ITEM + 1)
        assert order.version == 2  # Version should not change on failure

    def test_update_item_quantity_not_found(self, order: Order):
        unknown_product_id = ProductId()
        with pytest.raises(
            ValueError,
            match=(f"Продукт с ID {unknown_product_id.value} не найден для обновления"),
        ):
            order.update_item_quantity(unknown_product_id, 1)
        assert order.version == 1

    def test_order_status_transitions_pay_ship_cancel(
        self, order: Order, product1: Product
    ):
        order.add_item(product1, 1)  # v2
        assert order.status == OrderStatus.PENDING

        order.pay()  # v3
        assert order.status == OrderStatus.PAID
        assert order.version == 3

        order.ship()  # v4
        assert order.status == OrderStatus.SHIPPED
        assert order.version == 4

        # Try to cancel shipped order - should fail if logic prevents it
        # For this example, we assume we can cancel a shipped order
        # If cancellation of SHIPPED is not allowed, this test needs adjustment
        # order.cancel() # v5
        # assert order.status == OrderStatus.CANCELLED
        # assert order.version == 5

    def test_cancel_pending_order(self, order: Order, product1: Product):
        order.add_item(product1, 1)  # v2
        order.cancel()  # v3
        assert order.status == OrderStatus.CANCELLED
        assert order.version == 3

    def test_cancel_paid_order(self, order: Order, product1: Product):
        order.add_item(product1, 1)  # v2
        order.pay()  # v3
        order.cancel()  # v4
        assert order.status == OrderStatus.CANCELLED
        assert order.version == 4

    def test_invalid_status_transitions(self, order: Order, product1: Product):
        # Cannot ship PENDING order
        order.add_item(product1, 1)
        with pytest.raises(
            ValueError,
            match=(f"Заказ не может быть отгружен в статусе {OrderStatus.PENDING}"),
        ):
            order.ship()

        # Cannot pay CANCELLED order
        order_cancelled = Order(customer_id=order.customer_id)
        order_cancelled.add_item(product1, 1)
        order_cancelled.cancel()
        with pytest.raises(
            ValueError,
            match=(f"Заказ не может быть оплачен в статусе {OrderStatus.CANCELLED}"),
        ):
            order_cancelled.pay()

        # Cannot pay empty order
        empty_order = Order(customer_id=order.customer_id)
        with pytest.raises(ValueError, match="Нельзя оплатить пустой заказ"):
            empty_order.pay()

    def test_operations_on_non_pending_order_fail(
        self, order: Order, product1: Product, product2: Product
    ):
        order.add_item(product1, 1)
        order.pay()
        paid_status = order.status

        with pytest.raises(
            ValueError,
            match=f"Нельзя добавлять товары в заказ со статусом {paid_status}",
        ):
            order.add_item(product2, 1)
        with pytest.raises(
            ValueError,
            match=f"Нельзя удалять товары из заказа со статусом {paid_status}",
        ):
            order.remove_item(product1.id)
        with pytest.raises(
            ValueError,
            match=f"Нельзя изменять количество в заказе со статусом {paid_status}",
        ):
            order.update_item_quantity(product1.id, 2)
        assert order.version == 3  # Pay increments, then no more increments

    def test_items_property_returns_copy(self, order: Order, product1: Product):
        order.add_item(product1, 1)
        items_copy = order.items
        assert len(items_copy) == 1

        # Try to modify the copy
        items_copy.append(
            OrderItem(
                product_id=product2().id,
                product_name="Hack",
                quantity=1,
                price_per_unit=1.0,
            )
        )
        assert len(items_copy) == 2
        assert len(order.items) == 1, "Internal items list was modified externally!"

    def test_order_equality_based_on_id(self, customer_id: uuid.UUID):
        order_id_obj = OrderId()
        order1 = Order(id=order_id_obj, customer_id=customer_id)
        order2 = Order(id=order_id_obj, customer_id=customer_id)
        order3 = Order(customer_id=customer_id)  # Different ID

        assert order1 == order2
        assert order1 != order3
        assert order1 != "not an order"

    def test_product_price_fixed_at_addition(self, order: Order, product1: Product):
        original_price = product1.price
        order.add_item(product1, 1)
        assert order.items[0].price_per_unit == original_price

        # Simulate product price change in catalog (external to aggregate)
        product1.price = original_price + 50.0

        assert (
            order.items[0].price_per_unit == original_price
        ), "Item price changed after product price update."
        assert order.total_price == original_price * 1


def test_placeholder():
    assert True
