"""Tests for SQL repositories error handling."""

import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from sqlalchemy.exc import IntegrityError, DataError, SQLAlchemyError
from src.shared.infrastructure.sql_repositories import SQLRepository, SQLRepositoryWithRelations
from src.shared.domain.exceptions import EntityNotFoundError, InvalidOperationError


class TestSQLRepositoryErrorHandling:
    """Test SQLRepository error handling."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_session = AsyncMock()
        # Create a proper mock model class with id attribute
        self.mock_model = Mock()
        self.mock_model.id = Mock()
        # Mock the select statement to avoid ArgumentError
        with patch('src.shared.infrastructure.sql_repositories.select') as mock_select:
            mock_select.return_value.where.return_value = Mock()
        # Set up sync methods that should not be async
        self.mock_session.add = Mock()
        self.mock_session.delete = Mock()
        self.repository = SQLRepository(self.mock_session, self.mock_model)

    @pytest.mark.asyncio
    async def test_save_integrity_error(self):
        """Test save method with IntegrityError."""
        # Arrange
        entity = Mock()
        self.mock_session.add.side_effect = IntegrityError("", "", "")
        
        # Act & Assert
        with pytest.raises(IntegrityError):
            await self.repository.save(entity)

    @pytest.mark.asyncio
    async def test_save_data_error(self):
        """Test save method with DataError."""
        # Arrange
        entity = Mock()
        self.mock_session.add.side_effect = DataError("", "", "")
        
        # Act & Assert
        with pytest.raises(DataError):
            await self.repository.save(entity)

    @pytest.mark.asyncio
    async def test_save_sqlalchemy_error(self):
        """Test save method with SQLAlchemyError."""
        # Arrange
        entity = Mock()
        self.mock_session.add.side_effect = SQLAlchemyError("Database error")
        
        # Act & Assert
        with pytest.raises(SQLAlchemyError):
            await self.repository.save(entity)

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self):
        """Test get_by_id method when entity not found."""
        # Arrange
        entity_id = "test-id"
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        self.mock_session.execute.return_value = mock_result
        
        # Act & Assert
        result = await self.repository.get_by_id(entity_id)
        assert result is None

    @pytest.mark.asyncio
    async def test_get_by_id_sqlalchemy_error(self):
        """Test get_by_id method with SQLAlchemyError."""
        # Arrange
        entity_id = "test-id"
        self.mock_session.execute.side_effect = SQLAlchemyError("Database error")
        
        # Act & Assert
        with pytest.raises(SQLAlchemyError):
            await self.repository.get_by_id(entity_id)

    @pytest.mark.asyncio
    async def test_delete_not_found(self):
        """Test delete method when entity not found."""
        # Arrange
        entity_id = "test-id"
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        self.mock_session.execute.return_value = mock_result
        
        # Act & Assert
        result = await self.repository.delete(entity_id)
        assert result is False

    @pytest.mark.asyncio
    async def test_delete_sqlalchemy_error(self):
        """Test delete method with SQLAlchemyError."""
        # Arrange
        entity_id = "test-id"
        entity = Mock()
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = entity
        self.mock_session.execute.return_value = mock_result
        self.mock_session.delete.side_effect = SQLAlchemyError("Database error")
        
        # Act & Assert
        with pytest.raises(SQLAlchemyError):
            await self.repository.delete(entity_id)

    @pytest.mark.asyncio
    async def test_update_sqlalchemy_error(self):
        """Test update method with SQLAlchemyError."""
        # Arrange
        entity = Mock()
        self.mock_session.flush.side_effect = SQLAlchemyError("Database error")
        
        # Act & Assert
        with pytest.raises(SQLAlchemyError):
            await self.repository.update(entity)

    @pytest.mark.asyncio
    async def test_count_sqlalchemy_error(self):
        """Test count method with SQLAlchemyError."""
        # Arrange
        self.mock_session.execute.side_effect = SQLAlchemyError("Database error")
        
        # Act & Assert
        with pytest.raises(SQLAlchemyError):
            await self.repository.count()

    @pytest.mark.asyncio
    async def test_get_all_sqlalchemy_error(self):
        """Test get_all method with SQLAlchemyError."""
        # Arrange
        self.mock_session.execute.side_effect = SQLAlchemyError("Database error")
        
        # Act & Assert
        with pytest.raises(SQLAlchemyError):
            await self.repository.get_all()


class TestSQLRepositoryWithRelationsErrorHandling:
    """Test SQLRepositoryWithRelations error handling."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_session = AsyncMock()
        # Create a proper mock model class with id attribute
        self.mock_model = Mock()
        self.mock_model.id = Mock()
        # Mock the select statement to avoid ArgumentError
        with patch('src.shared.infrastructure.sql_repositories.select') as mock_select:
            mock_select.return_value.where.return_value = Mock()
        # Set up sync methods that should not be async
        self.mock_session.add = Mock()
        self.mock_session.delete = Mock()
        self.relations = ["relation1", "relation2"]
        self.repository = SQLRepositoryWithRelations(self.mock_session, self.mock_model, self.relations)

    @pytest.mark.asyncio
    async def test_get_by_id_with_relations_not_found(self):
        """Test get_by_id_with_relations method when entity not found."""
        # Arrange
        entity_id = "test-id"
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        self.mock_session.execute.return_value = mock_result
        
        # Act & Assert
        result = await self.repository.get_by_id_with_relations(entity_id)
        assert result is None

    @pytest.mark.asyncio
    async def test_get_by_id_with_relations_sqlalchemy_error(self):
        """Test get_by_id_with_relations method with SQLAlchemyError."""
        # Arrange
        entity_id = "test-id"
        self.mock_session.execute.side_effect = SQLAlchemyError("Database error")
        
        # Act & Assert
        with pytest.raises(SQLAlchemyError):
            await self.repository.get_by_id_with_relations(entity_id)

    @pytest.mark.asyncio
    async def test_get_all_with_relations_sqlalchemy_error(self):
        """Test get_all_with_relations method with SQLAlchemyError."""
        # Arrange
        self.mock_session.execute.side_effect = SQLAlchemyError("Database error")
        
        # Act & Assert
        with pytest.raises(SQLAlchemyError):
            await self.repository.get_all_with_relations()

    @pytest.mark.asyncio
    async def test_get_all_with_relations_empty_result(self):
        """Test get_all_with_relations method with empty result."""
        # Arrange
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = []
        self.mock_session.execute.return_value = mock_result
        
        # Act & Assert
        result = await self.repository.get_all_with_relations()
        assert result == [] 