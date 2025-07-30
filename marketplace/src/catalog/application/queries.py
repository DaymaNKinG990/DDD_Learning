"""CQRS queries for catalog bounded context."""

# Python imports
from abc import ABC, abstractmethod
from typing import List, Optional

from pydantic import BaseModel


# Query Models (Read Models)
class ProductReadModel(BaseModel):
    """
    Read model for product queries.
    
    Attributes:
        id: The product ID.
        name: The product name.
        description: The product description.
        price: The product price.
        category_id: The category ID.
        category_name: The category name.
        brand_id: The brand ID.
        brand_name: The brand name.
        sku: The product SKU.
        is_active: Whether the product is active.
    """

    id: str
    name: str
    description: str
    price: str
    category_id: str
    category_name: Optional[str] = None
    brand_id: Optional[str] = None
    brand_name: Optional[str] = None
    sku: str
    is_active: bool


class CategoryReadModel(BaseModel):
    """
    Read model for category queries.
    
    Attributes:
        id: The category ID.
        name: The category name.
        description: The category description.
        parent_id: The parent category ID.
        parent_name: The parent category name.
        product_count: The number of products in the category.
    """

    id: str
    name: str
    description: Optional[str] = None
    parent_id: Optional[str] = None
    parent_name: Optional[str] = None
    product_count: int = 0


class BrandReadModel(BaseModel):
    """
    Read model for brand queries.
    
    Attributes:
        id: The brand ID.
        name: The brand name.
        description: The brand description.
        logo_url: The brand logo URL.
        product_count: The number of products in the brand.
    """
    id: str
    name: str
    description: Optional[str] = None
    logo_url: Optional[str] = None
    product_count: int = 0


# Query Objects
class GetProductQuery(BaseModel):
    """
    Query to get a product by ID.
    
    Attributes:
        product_id: The ID of the product to get.
    """

    product_id: str


class GetProductsByCategoryQuery(BaseModel):
    """
    Query to get products by category.
    
    Attributes:
        category_id: The ID of the category to get products for.
        limit: The maximum number of products to return.
        offset: The offset to start from.
    """

    category_id: str
    limit: Optional[int] = 50
    offset: Optional[int] = 0


class GetProductsByBrandQuery(BaseModel):
    """
    Query to get products by brand.
    
    Attributes:
        brand_id: The ID of the brand to get products for.
        limit: The maximum number of products to return.
        offset: The offset to start from.
    """

    brand_id: str
    limit: Optional[int] = 50
    offset: Optional[int] = 0


class SearchProductsQuery(BaseModel):
    """
    Query to search products.
    
    Attributes:
        search_term: The search term.
        category_id: The ID of the category to filter by.
        brand_id: The ID of the brand to filter by.
        min_price: The minimum price to filter by.
        max_price: The maximum price to filter by.
        limit: The maximum number of products to return.
        offset: The offset to start from.
    """

    search_term: str
    category_id: Optional[str] = None
    brand_id: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    limit: Optional[int] = 50
    offset: Optional[int] = 0


class GetCategoryQuery(BaseModel):
    """
    Query to get a category by ID.
    
    Attributes:
        category_id: The ID of the category to get.
    """

    category_id: str


class GetCategoriesQuery(BaseModel):
    """
    Query to get all categories.
    
    Attributes:
        parent_id: The ID of the parent category to get subcategories for.
        include_inactive: Whether to include inactive categories.
    """

    parent_id: Optional[str] = None
    include_inactive: bool = False


class GetBrandQuery(BaseModel):
    """
    Query to get a brand by ID.
    
    Attributes:
        brand_id: The ID of the brand to get.
    """

    brand_id: str


class GetBrandsQuery(BaseModel):
    """
    Query to get all brands.
    
    Attributes:
        include_inactive: Whether to include inactive brands.
    """

    include_inactive: bool = False


# Query Handlers
class ProductQueryHandler(ABC):
    """
    Abstract query handler for product queries.
    
    This interface defines the methods for handling product queries.
    """

    @abstractmethod
    async def get_product(self, query: GetProductQuery) -> Optional[ProductReadModel]:
        """
        Get product by ID.
        
        Args:
            query: The query to get the product.
            
        Returns:
            Optional[ProductReadModel]: The product if found, None otherwise.
        """
        pass

    @abstractmethod
    async def get_products_by_category(
        self, query: GetProductsByCategoryQuery
    ) -> List[ProductReadModel]:
        """
        Get products by category.
        
        Args:
            query: The query to get the products.
            
        Returns:
            List[ProductReadModel]: The list of products.
        """
        pass

    @abstractmethod
    async def get_products_by_brand(
        self, query: GetProductsByBrandQuery
    ) -> List[ProductReadModel]:
        """
        Get products by brand.
        
        Args:
            query: The query to get the products.
            
        Returns:
            List[ProductReadModel]: The list of products.
        """
        pass

    @abstractmethod
    async def search_products(
        self, query: SearchProductsQuery
    ) -> List[ProductReadModel]:
        """
        Search products.
        
        Args:
            query: The query to search the products.
            
        Returns:
            List[ProductReadModel]: The list of products.
        """
        pass


class CategoryQueryHandler(ABC):
    """Abstract query handler for category queries.
    
    This interface defines the methods for handling category queries.
    """

    @abstractmethod
    async def get_category(
        self, query: GetCategoryQuery
    ) -> Optional[CategoryReadModel]:
        """
        Get category by ID.
        
        Args:
            query: The query to get the category.
            
        Returns:
            Optional[CategoryReadModel]: The category if found, None otherwise.
        """
        pass

    @abstractmethod
    async def get_categories(
        self, query: GetCategoriesQuery
    ) -> List[CategoryReadModel]:
        """
        Get categories.
        
        Args:
            query: The query to get the categories.
            
        Returns:
            List[CategoryReadModel]: The list of categories.
        """
        pass


class BrandQueryHandler(ABC):
    """
    Abstract query handler for brand queries.
    
    This interface defines the methods for handling brand queries.
    """

    @abstractmethod
    async def get_brand(self, query: GetBrandQuery) -> Optional[BrandReadModel]:
        """
        Get brand by ID.
        
        Args:
            query: The query to get the brand.
            
        Returns:
            Optional[BrandReadModel]: The brand if found, None otherwise.
        """
        pass

    @abstractmethod
    async def get_brands(self, query: GetBrandsQuery) -> List[BrandReadModel]:
        """
        Get brands.
        
        Args:
            query: The query to get the brands.
            
        Returns:
            List[BrandReadModel]: The list of brands.
        """
        pass


# In-Memory Query Handlers (for testing/demo)
class InMemoryProductQueryHandler(ProductQueryHandler):
    """
    In-memory implementation of product query handler.
    
    This class provides an in-memory implementation of the product query handler.
    """

    def __init__(self) -> None:
        """Initialize the in-memory product query handler."""
        self._products: dict[str, ProductReadModel] = {}
        self._categories: dict[str, CategoryReadModel] = {}
        self._brands: dict[str, BrandReadModel] = {}

    async def get_product(self, query: GetProductQuery) -> Optional[ProductReadModel]:
        """
        Get product by ID.
        
        Args:
            query: The query to get the product.
            
        Returns:
            Optional[ProductReadModel]: The product if found, None otherwise.
        """
        return self._products.get(query.product_id)

    async def get_products_by_category(
        self,
        query: GetProductsByCategoryQuery
    ) -> List[ProductReadModel]:
        """
        Get products by category.
        
        Args:
            query: The query to get the products.
            
        Returns:
            List[ProductReadModel]: The list of products.
        """
        products = [
            product for product in self._products.values()
            if product.category_id == query.category_id and product.is_active
        ]

        # Apply pagination
        start = query.offset or 0
        end = start + (query.limit or 50)
        return products[start:end]

    async def get_products_by_brand(
        self,
        query: GetProductsByBrandQuery
    ) -> List[ProductReadModel]:
        """
        Get products by brand.
        
        Args:
            query: The query to get the products.
            
        Returns:
            List[ProductReadModel]: The list of products.
        """
        products = [
            product for product in self._products.values()
            if product.brand_id == query.brand_id and product.is_active
        ]

        # Apply pagination
        start = query.offset or 0
        end = start + (query.limit or 50)
        return products[start:end]

    async def search_products(
        self,
        query: SearchProductsQuery
    ) -> List[ProductReadModel]:
        """
        Search products.
        
        Args:
            query: The query to search the products.
            
        Returns:
            List[ProductReadModel]: The list of products.
        """
        products = [
            product for product in self._products.values()
            if product.is_active and self._matches_search_criteria(product, query)
        ]

        # Apply pagination
        start = query.offset or 0
        end = start + (query.limit or 50)
        return products[start:end]

    def _matches_search_criteria(
        self,
        product: ProductReadModel,
        query: SearchProductsQuery
    ) -> bool:
        """
        Check if product matches search criteria.
        
        Args:
            product: The product to check.
            query: The query to search the products.
            
        Returns:
            bool: True if the product matches the search criteria, False otherwise.
        """
        # Search term matching
        if query.search_term:
            search_lower = query.search_term.lower()
            if (search_lower not in product.name.lower() and
                search_lower not in product.description.lower()):
                return False

        # Category filter
        if query.category_id and product.category_id != query.category_id:
            return False

        # Brand filter
        if query.brand_id and product.brand_id != query.brand_id:
            return False

        # Price range filter
        try:
            price = float(product.price.replace("RUB", "").strip())
            if query.min_price and price < query.min_price:
                return False
            if query.max_price and price > query.max_price:
                return False
        except ValueError:
            pass

        return True

    def add_product(self, product: ProductReadModel) -> None:
        """
        Add product to in-memory storage.
        
        Args:
            product: The product to add.
        """
        self._products[product.id] = product

    def add_category(self, category: CategoryReadModel) -> None:
        """
        Add category to in-memory storage.
        
        Args:
            category: The category to add.
        """
        self._categories[category.id] = category

    def add_brand(self, brand: BrandReadModel) -> None:
        """
        Add brand to in-memory storage.
        
        Args:
            brand: The brand to add.
        """
        self._brands[brand.id] = brand


class InMemoryCategoryQueryHandler(CategoryQueryHandler):
    """
    In-memory implementation of category query handler.
    
    This class provides an in-memory implementation of the category query handler.
    """

    def __init__(self) -> None:
        """Initialize the in-memory category query handler."""
        self._categories: dict[str, CategoryReadModel] = {}

    async def get_category(
        self,
        query: GetCategoryQuery
    ) -> Optional[CategoryReadModel]:
        """
        Get category by ID.
        
        Args:
            query: The query to get the category.
            
        Returns:
            Optional[CategoryReadModel]: The category if found, None otherwise.
        """
        return self._categories.get(query.category_id)

    async def get_categories(
        self,
        query: GetCategoriesQuery
    ) -> List[CategoryReadModel]:
        """Get categories.
        
        Args:
            query: The query to get the categories.
            
        Returns:
            List[CategoryReadModel]: The list of categories.
        """
        categories = list(self._categories.values())

        if query.parent_id is not None:
            categories = [cat for cat in categories if cat.parent_id == query.parent_id]

        return categories

    def add_category(self, category: CategoryReadModel) -> None:
        """Add category to in-memory storage.
        
        Args:
            category: The category to add.
        """
        self._categories[category.id] = category


class InMemoryBrandQueryHandler(BrandQueryHandler):
    """
    In-memory implementation of brand query handler.
    
    This class provides an in-memory implementation of the brand query handler.
    """

    def __init__(self) -> None:
        """Initialize the in-memory brand query handler."""
        self._brands: dict[str, BrandReadModel] = {}

    async def get_brand(self, query: GetBrandQuery) -> Optional[BrandReadModel]:
        """
        Get brand by ID.
        
        Args:
            query: The query to get the brand.
            
        Returns:
            Optional[BrandReadModel]: The brand if found, None otherwise.
        """
        return self._brands.get(query.brand_id)

    async def get_brands(self, query: GetBrandsQuery) -> List[BrandReadModel]:
        """
        Get brands.
        
        Args:
            query: The query to get the brands.
            
        Returns:
            List[BrandReadModel]: The list of brands.
        """
        return list(self._brands.values())

    def add_brand(self, brand: BrandReadModel) -> None:
        """
        Add brand to in-memory storage.
        
        Args:
            brand: The brand to add.
        """
        self._brands[brand.id] = brand
