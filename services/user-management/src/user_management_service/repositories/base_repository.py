"""
Base repository interface and implementation for the User Management Service.
"""

import json
import os
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, TypeVar, Generic
from uuid import UUID

from ..utils.exceptions import RepositoryError, NotFoundError, DuplicateError

T = TypeVar('T')


class BaseRepository(ABC, Generic[T]):
    """Abstract base repository interface."""
    
    @abstractmethod
    def create(self, entity: T) -> T:
        """Create a new entity."""
        pass
    
    @abstractmethod
    def find_by_id(self, entity_id: UUID) -> Optional[T]:
        """Find entity by ID."""
        pass
    
    @abstractmethod
    def find_all(self) -> List[T]:
        """Find all entities."""
        pass
    
    @abstractmethod
    def update(self, entity: T) -> T:
        """Update an existing entity."""
        pass
    
    @abstractmethod
    def delete(self, entity_id: UUID) -> bool:
        """Delete an entity by ID."""
        pass
    
    @abstractmethod
    def exists(self, entity_id: UUID) -> bool:
        """Check if entity exists."""
        pass


class InMemoryRepository(BaseRepository[T]):
    """In-memory repository implementation with file persistence."""
    
    def __init__(self, entity_type: str, data_file: Optional[str] = None):
        """Initialize the repository."""
        self.entity_type = entity_type
        self.data_file = data_file or f"{entity_type.lower()}_data.json"
        self._data: Dict[str, T] = {}
        self._load_data()
    
    def _get_data_directory(self) -> str:
        """Get the data directory path."""
        data_dir = os.path.join(os.getcwd(), "user_management_service", "data")
        os.makedirs(data_dir, exist_ok=True)
        return data_dir
    
    def _get_file_path(self) -> str:
        """Get the full file path for data persistence."""
        return os.path.join(self._get_data_directory(), self.data_file)
    
    def _load_data(self) -> None:
        """Load data from file."""
        try:
            file_path = self._get_file_path()
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Convert dict data back to entities using from_dict method
                    for entity_id, entity_data in data.items():
                        try:
                            # This assumes entities have a from_dict class method
                            entity = self._deserialize_entity(entity_data)
                            self._data[entity_id] = entity
                        except Exception as e:
                            print(f"Warning: Failed to load entity {entity_id}: {e}")
        except Exception as e:
            print(f"Warning: Failed to load data from {self.data_file}: {e}")
    
    def _save_data(self) -> None:
        """Save data to file."""
        try:
            file_path = self._get_file_path()
            data = {}
            for entity_id, entity in self._data.items():
                try:
                    # This assumes entities have a to_dict method
                    data[entity_id] = entity.to_dict()
                except Exception as e:
                    print(f"Warning: Failed to serialize entity {entity_id}: {e}")
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Warning: Failed to save data to {self.data_file}: {e}")
    
    def _deserialize_entity(self, data: Dict[str, Any]) -> T:
        """Deserialize entity from dictionary data."""
        # This method should be overridden in concrete repositories
        # to handle specific entity deserialization
        raise NotImplementedError("Subclasses must implement _deserialize_entity")
    
    def create(self, entity: T) -> T:
        """Create a new entity."""
        try:
            entity_id = str(entity.id)
            if entity_id in self._data:
                raise DuplicateError(
                    f"{self.entity_type} with ID {entity_id} already exists",
                    self.entity_type,
                    "id",
                    entity_id
                )
            
            self._data[entity_id] = entity
            self._save_data()
            return entity
        except Exception as e:
            if isinstance(e, DuplicateError):
                raise
            raise RepositoryError(
                f"Failed to create {self.entity_type}: {str(e)}",
                self.entity_type,
                entity.id if hasattr(entity, 'id') else None
            )
    
    def find_by_id(self, entity_id: UUID) -> Optional[T]:
        """Find entity by ID."""
        try:
            return self._data.get(str(entity_id))
        except Exception as e:
            raise RepositoryError(
                f"Failed to find {self.entity_type} by ID: {str(e)}",
                self.entity_type,
                entity_id
            )
    
    def find_all(self) -> List[T]:
        """Find all entities."""
        try:
            return list(self._data.values())
        except Exception as e:
            raise RepositoryError(
                f"Failed to find all {self.entity_type}: {str(e)}",
                self.entity_type
            )
    
    def update(self, entity: T) -> T:
        """Update an existing entity."""
        try:
            entity_id = str(entity.id)
            if entity_id not in self._data:
                raise NotFoundError(
                    f"{self.entity_type} with ID {entity_id} not found",
                    self.entity_type,
                    entity.id
                )
            
            self._data[entity_id] = entity
            self._save_data()
            return entity
        except Exception as e:
            if isinstance(e, NotFoundError):
                raise
            raise RepositoryError(
                f"Failed to update {self.entity_type}: {str(e)}",
                self.entity_type,
                entity.id if hasattr(entity, 'id') else None
            )
    
    def delete(self, entity_id: UUID) -> bool:
        """Delete an entity by ID."""
        try:
            entity_id_str = str(entity_id)
            if entity_id_str not in self._data:
                return False
            
            del self._data[entity_id_str]
            self._save_data()
            return True
        except Exception as e:
            raise RepositoryError(
                f"Failed to delete {self.entity_type}: {str(e)}",
                self.entity_type,
                entity_id
            )
    
    def exists(self, entity_id: UUID) -> bool:
        """Check if entity exists."""
        try:
            return str(entity_id) in self._data
        except Exception as e:
            raise RepositoryError(
                f"Failed to check existence of {self.entity_type}: {str(e)}",
                self.entity_type,
                entity_id
            )
    
    def count(self) -> int:
        """Get the total count of entities."""
        try:
            return len(self._data)
        except Exception as e:
            raise RepositoryError(
                f"Failed to count {self.entity_type}: {str(e)}",
                self.entity_type
            )
    
    def clear(self) -> None:
        """Clear all data (useful for testing)."""
        try:
            self._data.clear()
            self._save_data()
        except Exception as e:
            raise RepositoryError(
                f"Failed to clear {self.entity_type} data: {str(e)}",
                self.entity_type
            )
    
    def find_by_field(self, field_name: str, value: Any) -> List[T]:
        """Find entities by a specific field value."""
        try:
            results = []
            for entity in self._data.values():
                if hasattr(entity, field_name) and getattr(entity, field_name) == value:
                    results.append(entity)
            return results
        except Exception as e:
            raise RepositoryError(
                f"Failed to find {self.entity_type} by {field_name}: {str(e)}",
                self.entity_type
            )
    
    def find_by_fields(self, criteria: Dict[str, Any]) -> List[T]:
        """Find entities by multiple field criteria."""
        try:
            results = []
            for entity in self._data.values():
                match = True
                for field_name, value in criteria.items():
                    if not hasattr(entity, field_name) or getattr(entity, field_name) != value:
                        match = False
                        break
                if match:
                    results.append(entity)
            return results
        except Exception as e:
            raise RepositoryError(
                f"Failed to find {self.entity_type} by criteria: {str(e)}",
                self.entity_type
            )