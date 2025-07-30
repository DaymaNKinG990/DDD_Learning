"""CQRS queries for orders bounded context."""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


# Query Models (Read Models)
class OrderReadModel(BaseModel):
    """Read model for order queries."""

    id: str
    customer_id: str
    customer_name: Optional[str] = None
    status: str
    total: str
    shipping_address: str
    billing_address: str
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    items: List["OrderItemReadModel"] = []


class OrderItemReadModel(BaseModel):
    """Read model for order item queries."""

    id: str
    order_id: str
    product_id: str
    product_name: str
    quantity: int
    unit_price: str
    total: str


class OrderSummaryReadModel(BaseModel):
    """Read model for order summary queries."""

    id: str
    customer_id: str
    status: str
    total: str
    item_count: int
    created_at: datetime


# Query Objects
class GetOrderQuery(BaseModel):
    """Query to get an order by ID."""

    order_id: str


class GetOrdersByCustomerQuery(BaseModel):
    """Query to get orders by customer."""

    customer_id: str
    limit: Optional[int] = 50
    offset: Optional[int] = 0
    status: Optional[str] = None


class GetOrdersByStatusQuery(BaseModel):
    """Query to get orders by status."""

    status: str
    limit: Optional[int] = 50
    offset: Optional[int] = 0


class GetOrdersByDateRangeQuery(BaseModel):
    """Query to get orders by date range."""

    start_date: datetime
    end_date: datetime
    limit: Optional[int] = 50
    offset: Optional[int] = 0


class GetOrderSummaryQuery(BaseModel):
    """Query to get order summary."""

    order_id: str


class GetCustomerOrderHistoryQuery(BaseModel):
    """Query to get customer order history."""

    customer_id: str
    limit: Optional[int] = 50
    offset: Optional[int] = 0


# Query Handlers
class OrderQueryHandler(ABC):
    """Abstract query handler for order queries."""

    @abstractmethod
    async def get_order(self, query: GetOrderQuery) -> Optional[OrderReadModel]:
        """Get order by ID."""
        pass

    @abstractmethod
    async def get_orders_by_customer(
        self, query: GetOrdersByCustomerQuery
    ) -> List[OrderReadModel]:
        """Get orders by customer."""
        pass

    @abstractmethod
    async def get_orders_by_status(
        self, query: GetOrdersByStatusQuery
    ) -> List[OrderReadModel]:
        """Get orders by status."""
        pass

    @abstractmethod
    async def get_orders_by_date_range(
        self, query: GetOrdersByDateRangeQuery
    ) -> List[OrderReadModel]:
        """Get orders by date range."""
        pass

    @abstractmethod
    async def get_order_summary(
        self, query: GetOrderSummaryQuery
    ) -> Optional[OrderSummaryReadModel]:
        """Get order summary."""
        pass

    @abstractmethod
    async def get_customer_order_history(
        self, query: GetCustomerOrderHistoryQuery
    ) -> List[OrderSummaryReadModel]:
        """Get customer order history."""
        pass


# In-Memory Query Handler (for testing/demo)
class InMemoryOrderQueryHandler(OrderQueryHandler):
    """In-memory implementation of order query handler."""

    def __init__(self):
        self._orders: dict[str, OrderReadModel] = {}
        self._order_summaries: dict[str, OrderSummaryReadModel] = {}

    async def get_order(self, query: GetOrderQuery) -> Optional[OrderReadModel]:
        """Get order by ID."""
        return self._orders.get(query.order_id)

    async def get_orders_by_customer(
        self, query: GetOrdersByCustomerQuery
    ) -> List[OrderReadModel]:
        """Get orders by customer."""
        orders = [
            order for order in self._orders.values()
            if order.customer_id == query.customer_id
        ]
        start = (query.page - 1) * query.page_size
        end = start + query.page_size
        return orders[start:end]

    async def get_orders_by_status(
        self, query: GetOrdersByStatusQuery
    ) -> List[OrderReadModel]:
        """Get orders by status."""
        orders = [
            order for order in self._orders.values()
            if order.status == query.status
        ]
        start = (query.page - 1) * query.page_size
        end = start + query.page_size
        return orders[start:end]

    async def get_orders_by_date_range(
        self, query: GetOrdersByDateRangeQuery
    ) -> List[OrderReadModel]:
        """Get orders by date range."""
        orders = [
            order for order in self._orders.values()
            if query.start_date <= order.created_at <= query.end_date
        ]
        start = (query.page - 1) * query.page_size
        end = start + query.page_size
        return orders[start:end]

    async def get_order_summary(
        self, query: GetOrderSummaryQuery
    ) -> Optional[OrderSummaryReadModel]:
        """Get order summary."""
        return self._order_summaries.get(query.order_id)

    async def get_customer_order_history(
        self, query: GetCustomerOrderHistoryQuery
    ) -> List[OrderSummaryReadModel]:
        """Get customer order history."""
        summaries = [
            summary for summary in self._order_summaries.values()
            if summary.customer_id == query.customer_id
        ]

        # Sort by creation date (newest first)
        summaries.sort(key=lambda x: x.created_at, reverse=True)

        # Apply pagination
        start = query.offset or 0
        end = start + (query.limit or 50)
        return summaries[start:end]

    def add_order(self, order: OrderReadModel) -> None:
        """Add order to in-memory storage."""
        self._orders[order.id] = order

        # Create order summary
        summary = OrderSummaryReadModel(
            id=order.id,
            customer_id=order.customer_id,
            status=order.status,
            total=order.total,
            item_count=len(order.items),
            created_at=order.created_at
        )
        self._order_summaries[order.id] = summary

    def update_order(self, order: OrderReadModel) -> None:
        """Update order in in-memory storage."""
        self._orders[order.id] = order

        # Update order summary
        if order.id in self._order_summaries:
            summary = self._order_summaries[order.id]
            summary.status = order.status
            summary.total = order.total
            summary.item_count = len(order.items)
            summary.created_at = order.created_at
