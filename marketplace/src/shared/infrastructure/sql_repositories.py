"""Base SQLAlchemy repository implementations."""

# Python imports
from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

# Local imports
from src.shared.infrastructure.models import Base


T = TypeVar("T", bound=Base)


class SQLRepository(ABC, Generic[T]):
    """
    Base SQLAlchemy repository implementation.
    
    Attributes:
        session: The SQLAlchemy session.
        model_class: The model class.
    """
    
    def __init__(self, session: AsyncSession, model_class: Type[T]) -> None:
        """
        Initialize the SQL repository.
        
        Args:
            session: The SQLAlchemy session.
            model_class: The model class.
        """
        self.session = session
        self.model_class = model_class
    
    async def save(self, entity: T) -> T:
        """
        Save entity to database.
        
        Args:
            entity: The entity to save.

        Returns:
            T: The saved entity.
        """
        self.session.add(entity)
        await self.session.flush()
        await self.session.refresh(entity)
        return entity
    
    async def get_by_id(self, entity_id: Any) -> Optional[T]:
        """
        Get entity by ID.
        
        Args:
            entity_id: The ID of the entity.

        Returns:
            Optional[T]: The entity if found, None otherwise.
        """
        stmt = select(self.model_class).where(self.model_class.id == entity_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_all(self) -> List[T]:
        """
        Get all entities.
        
        Returns:
            List[T]: The list of entities.
        """
        stmt = select(self.model_class)
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def delete(self, entity_id: Any) -> bool:
        """
        Delete entity by ID.
        
        Args:
            entity_id: The ID of the entity.

        Returns:
            bool: True if the entity was deleted, False otherwise.
        """
        entity = await self.get_by_id(entity_id)
        if entity:
            await self.session.delete(entity)
            return True
        return False
    
    async def update(self, entity: T) -> T:
        """
        Update entity.
        
        Args:
            entity: The entity to update.

        Returns:
            T: The updated entity.
        """
        await self.session.flush()
        await self.session.refresh(entity)
        return entity
    
    async def count(self) -> int:
        """
        Count total entities.
        
        Returns:
            int: The total number of entities.
        """
        stmt = select(self.model_class)
        result = await self.session.execute(stmt)
        return len(result.scalars().all())


class SQLRepositoryWithRelations(SQLRepository[T]):
    """
    SQLAlchemy repository with relationship loading support.
    
    Attributes:
        relations: The relations to load.
    """
    
    def __init__(self, session: AsyncSession, model_class: Type[T], relations: Optional[List[str]] = None) -> None:
        """
        Initialize the SQL repository with relations.
        
        Args:
            session: The SQLAlchemy session.
            model_class: The model class.
            relations: The relations to load.
        """
        super().__init__(session, model_class)
        self.relations = relations or []
    
    async def get_by_id_with_relations(self, entity_id: Any) -> Optional[T]:
        """
        Get entity by ID with loaded relations.
        
        Args:
            entity_id: The ID of the entity.

        Returns:
            Optional[T]: The entity if found, None otherwise.
        """
        stmt = select(self.model_class).where(self.model_class.id == entity_id)
        
        # Load relations
        for relation in self.relations:
            stmt = stmt.options(selectinload(getattr(self.model_class, relation)))
        
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_all_with_relations(self) -> List[T]:
        """
        Get all entities with loaded relations.
        
        Returns:
            List[T]: The list of entities.
        """
        stmt = select(self.model_class)
        
        # Load relations
        for relation in self.relations:
            stmt = stmt.options(selectinload(getattr(self.model_class, relation)))
        
        result = await self.session.execute(stmt)
        return result.scalars().all() 