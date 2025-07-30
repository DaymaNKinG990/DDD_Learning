"""Base SQLAlchemy repository implementations."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.shared.infrastructure.models import Base

T = TypeVar("T", bound=Base)


class SQLRepository(ABC, Generic[T]):
    """Base SQLAlchemy repository implementation."""
    
    def __init__(self, session: AsyncSession, model_class: Type[T]):
        self.session = session
        self.model_class = model_class
    
    async def save(self, entity: T) -> T:
        """Save entity to database."""
        self.session.add(entity)
        await self.session.flush()
        await self.session.refresh(entity)
        return entity
    
    async def get_by_id(self, entity_id: Any) -> Optional[T]:
        """Get entity by ID."""
        stmt = select(self.model_class).where(self.model_class.id == entity_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_all(self) -> List[T]:
        """Get all entities."""
        stmt = select(self.model_class)
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def delete(self, entity_id: Any) -> bool:
        """Delete entity by ID."""
        entity = await self.get_by_id(entity_id)
        if entity:
            await self.session.delete(entity)
            return True
        return False
    
    async def update(self, entity: T) -> T:
        """Update entity."""
        await self.session.flush()
        await self.session.refresh(entity)
        return entity
    
    async def count(self) -> int:
        """Count total entities."""
        stmt = select(self.model_class)
        result = await self.session.execute(stmt)
        return len(result.scalars().all())


class SQLRepositoryWithRelations(SQLRepository[T]):
    """SQLAlchemy repository with relationship loading support."""
    
    def __init__(self, session: AsyncSession, model_class: Type[T], relations: Optional[List[str]] = None):
        super().__init__(session, model_class)
        self.relations = relations or []
    
    async def get_by_id_with_relations(self, entity_id: Any) -> Optional[T]:
        """Get entity by ID with loaded relations."""
        stmt = select(self.model_class).where(self.model_class.id == entity_id)
        
        # Load relations
        for relation in self.relations:
            stmt = stmt.options(selectinload(getattr(self.model_class, relation)))
        
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_all_with_relations(self) -> List[T]:
        """Get all entities with loaded relations."""
        stmt = select(self.model_class)
        
        # Load relations
        for relation in self.relations:
            stmt = stmt.options(selectinload(getattr(self.model_class, relation)))
        
        result = await self.session.execute(stmt)
        return result.scalars().all() 