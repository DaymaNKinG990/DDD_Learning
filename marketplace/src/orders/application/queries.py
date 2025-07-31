"""CQRS queries for orders bounded context."""

# Python imports
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


# Query Models (Read Models)
class OrderReadModel(BaseModel):
    """
    Read model for order queries.
    
    This model represents the read model for an order.

    Attributes:
        id (str): The ID of the order.
        customer_id (str): The ID of the customer.
        customer_name (Optional[str]): The name of the customer.
        status (str): The status of the order.
        total (str): The total amount of the order.
        shipping_address (str): The shipping address of the order.
        billing_address (str): The billing address of the order.
        notes (Optional[str]): The notes of the order.
        created_at (datetime): The date and time the order was created.
        updated_at (datetime): The date and time the order was last updated.
        items (List[OrderItemReadModel]): The items in the order.
    """

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
    """
    Read model for order item queries.
    
    This model represents the read model for an order item.
    
    Attributes:
        id (str): The ID of the order item.
        order_id (str): The ID of the order.
        product_id (str): The ID of the product.
        product_name (str): The name of the product.
        quantity (int): The quantity of the product.
        unit_price (str): The price of the product per unit.
        total (str): The total price of the product.
    """

    id: str
    order_id: str
    product_id: str
    product_name: str
    quantity: int
    unit_price: str
    total: str


class OrderSummaryReadModel(BaseModel):
    """
    Read model for order summary queries.
    
    This model represents the read model for an order summary.
    
    Attributes:
        id (str): The ID of the order summary.
        customer_id (str): The ID of the customer.
        status (str): The status of the order.
        total (str): The total amount of the order.
        item_count (int): The number of items in the order.
        created_at (datetime): The date and time the order summary was created.
    """

    id: str
    customer_id: str
    status: str
    total: str
    item_count: int
    created_at: datetime


# Query Objects
class GetOrderQuery(BaseModel):
    """
    Query to get an order by ID.
    
    This query is used to get an order by its ID.
    
    Attributes:
        order_id (str): The ID of the order to get.
    """

    order_id: str


class GetOrdersByCustomerQuery(BaseModel):
    """
    Query to get orders by customer.
    
    This query is used to get all orders for a customer.
    
    Attributes:
        customer_id (str): The ID of the customer to get orders for.
        limit (Optional[int]): The maximum number of orders to return.
        offset (Optional[int]): The number of orders to skip.
    """

    customer_id: str
    limit: Optional[int] = 50
    offset: Optional[int] = 0
    status: Optional[str] = None


class GetOrdersByStatusQuery(BaseModel):
    """
    Query to get orders by status.
    
    This query is used to get all orders by a given status.
    
    Attributes:
        status (str): The status of the orders to get.
        limit (Optional[int]): The maximum number of orders to return.
        offset (Optional[int]): The number of orders to skip.
    """

    status: str
    limit: Optional[int] = 50
    offset: Optional[int] = 0


class GetOrdersByDateRangeQuery(BaseModel):
    """
    Query to get orders by date range.
    
    This query is used to get all orders within a given date range.
    
    Attributes:
        start_date (datetime): The start date of the date range.
        end_date (datetime): The end date of the date range.
        limit (Optional[int]): The maximum number of orders to return.
        offset (Optional[int]): The number of orders to skip.
    """

    start_date: datetime
    end_date: datetime
    limit: Optional[int] = 50
    offset: Optional[int] = 0


class GetOrderSummaryQuery(BaseModel):
    """
    Query to get order summary.
    
    This query is used to get the summary of an order.
    
    Attributes:
        order_id (str): The ID of the order to get the summary for.
    """

    order_id: str


class GetCustomerOrderHistoryQuery(BaseModel):
    """
    Query to get customer order history.
    
    This query is used to get the order history for a customer.
    
    Attributes:
        customer_id (str): The ID of the customer to get the order history for.
        limit (Optional[int]): The maximum number of orders to return.
        offset (Optional[int]): The number of orders to skip.
    """

    customer_id: str
    limit: Optional[int] = 50
    offset: Optional[int] = 0


# Query Handlers
class OrderQueryHandler(ABC):
    """
    Abstract query handler for order queries.
    
    This abstract class defines the interface for query handlers for order queries.
    """

    @abstractmethod
    async def get_order(self, query: GetOrderQuery) -> Optional[OrderReadModel]:
        """
        Get order by ID.
        
        Args:
            query (GetOrderQuery): The query to get an order by ID.

        Returns:
            Optional[OrderReadModel]: The order if found, None otherwise.
        """
        pass

    @abstractmethod
    async def get_orders_by_customer(self, query: GetOrdersByCustomerQuery) -> List[OrderReadModel]:
        """Get orders by customer.
        
        Args:
            query (GetOrdersByCustomerQuery): The query to get orders by customer.

        Returns:
            List[OrderReadModel]: The orders for the customer.
        """
        pass

    @abstractmethod
    async def get_orders_by_status(self, query: GetOrdersByStatusQuery) -> List[OrderReadModel]:
        """
        Get orders by status.
        
        Args:
            query (GetOrdersByStatusQuery): The query to get orders by status.

        Returns:
            List[OrderReadModel]: The orders with the given status.
        """
        pass

    @abstractmethod
    async def get_orders_by_date_range(self, query: GetOrdersByDateRangeQuery) -> List[OrderReadModel]:
        """
        Get orders by date range.
        
        Args:
            query (GetOrdersByDateRangeQuery): The query to get orders by date range.

        Returns:
            List[OrderReadModel]: The orders within the date range.
        """
        pass

    @abstractmethod
    async def get_order_summary(self, query: GetOrderSummaryQuery) -> Optional[OrderSummaryReadModel]:
        """
        Get order summary.
        
        Args:
            query (GetOrderSummaryQuery): The query to get the summary of an order.

        Returns:
            Optional[OrderSummaryReadModel]: The summary of the order if found, None otherwise.
        """
        pass

    @abstractmethod
    async def get_customer_order_history(self, query: GetCustomerOrderHistoryQuery) -> List[OrderSummaryReadModel]:
        """
        Get customer order history.
        
        Args:
            query (GetCustomerOrderHistoryQuery): The query to get the order history for a customer.

        Returns:
            List[OrderSummaryReadModel]: The order history for the customer.
        """
        pass


# In-Memory Query Handler (for testing/demo)
class InMemoryOrderQueryHandler(OrderQueryHandler):
    """
    In-memory implementation of order query handler.
    
    This class provides an in-memory implementation of the order query handler.
    """

    def __init__(self) -> None:
        """Initialize the in-memory order query handler."""
        self._orders: dict[str, OrderReadModel] = {}
        self._order_summaries: dict[str, OrderSummaryReadModel] = {}

    async def get_order(self, query: GetOrderQuery) -> Optional[OrderReadModel]:
        """
        Get order by ID.
        
        Args:
            query (GetOrderQuery): The query to get an order by ID.

        Returns:
            Optional[OrderReadModel]: The order if found, None otherwise.
        """
        return self._orders.get(query.order_id)

    async def get_orders_by_customer(self, query: GetOrdersByCustomerQuery) -> List[OrderReadModel]:
        """
        Get orders by customer.
        
        Args:
            query (GetOrdersByCustomerQuery): The query to get orders by customer.

        Returns:
            List[OrderReadModel]: The orders for the customer.
        """
        orders = [
            order for order in self._orders.values()
            if order.customer_id == query.customer_id
        ]

        # Apply status filter
        if query.status:
            orders = [order for order in orders if order.status == query.status]

        # Sort by creation date (newest first)
        orders.sort(key=lambda x: x.created_at, reverse=True)

        # Apply pagination
        start = query.offset or 0
        end = start + (query.limit or 50)
        return orders[start:end]

    async def get_orders_by_status(self, query: GetOrdersByStatusQuery) -> List[OrderReadModel]:
        """
        Get orders by status.
        
        Args:
            query (GetOrdersByStatusQuery): The query to get orders by status.

        Returns:
            List[OrderReadModel]: The orders with the given status.
        """
        orders = [
            order for order in self._orders.values()
            if order.status == query.status
        ]
        start = (query.page - 1) * query.page_size
        end = start + query.page_size
        return orders[start:end]

    async def get_orders_by_date_range(self, query: GetOrdersByDateRangeQuery) -> List[OrderReadModel]:
        """
        Get orders by date range.
        
        Args:
            query (GetOrdersByDateRangeQuery): The query to get orders by date range.

        Returns:
            List[OrderReadModel]: The orders within the date range.
        """
        orders = [
            order for order in self._orders.values()
            if query.start_date <= order.created_at <= query.end_date
        ]
        start = (query.page - 1) * query.page_size
        end = start + query.page_size
        return orders[start:end]

    async def get_order_summary(self, query: GetOrderSummaryQuery) -> Optional[OrderSummaryReadModel]:
        """
        Get order summary.
        
        Args:
            query (GetOrderSummaryQuery): The query to get the summary of an order.

        Returns:
            Optional[OrderSummaryReadModel]: The summary of the order if found, None otherwise.
        """
        return self._order_summaries.get(query.order_id)

    async def get_customer_order_history(self, query: GetCustomerOrderHistoryQuery) -> List[OrderSummaryReadModel]:
        """
        Get customer order history.
        
        Args:
            query (GetCustomerOrderHistoryQuery): The query to get the order history for a customer.

        Returns:
            List[OrderSummaryReadModel]: The order history for the customer.
        """
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
        """
        Add order to in-memory storage.
        
        Args:
            order (OrderReadModel): The order to add to in-memory storage.
        """
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
        """
        Update order in in-memory storage.
        
        Args:
            order (OrderReadModel): The order to update in in-memory storage.
        """
        self._orders[order.id] = order

        # Update order summary
        if order.id in self._order_summaries:
            summary = self._order_summaries[order.id]
            summary.status = order.status
            summary.total = order.total
            summary.item_count = len(order.items)
            summary.created_at = order.created_at
