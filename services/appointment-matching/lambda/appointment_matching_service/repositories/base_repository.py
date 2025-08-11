"""
Base repository interface and in-memory implementation.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, TypeVar, Generic, Callable
from datetime import datetime

from ..utils.helpers import generate_uuid, get_current_utc_datetime, setup_logging
from ..utils.exceptions import NotFoundError, ValidationError

T = TypeVar('T')


class BaseRepository(ABC, Generic[T]):
    """Abstract base repository interface."""
    
    @abstractmethod
    def create(self, entity: T) -> T:
        """Create a new entity."""
        pass
    
    @abstractmethod
    def find_by_id(self, entity_id: str) -> Optional[T]:
        """Find entity by ID."""
        pass
    
    @abstractmethod
    def find_all(self) -> List[T]:
        """Find all entities."""
        pass
    
    @abstractmethod
    def update(self, entity_id: str, entity: T) -> T:
        """Update an existing entity."""
        pass
    
    @abstractmethod
    def delete(self, entity_id: str) -> bool:
        """Delete an entity."""
        pass


class InMemoryRepository(BaseRepository[T]):
    """In-memory repository implementation."""
    
    def __init__(self, entity_name: str):
        self.entity_name = entity_name
        self._storage: Dict[str, T] = {}
        self.logger = setup_logging(f"{entity_name}Repository")
    
    def create(self, entity: T) -> T:
        """Create a new entity."""
        if not hasattr(entity, 'id') or not entity.id:
            entity.id = generate_uuid()
        
        if hasattr(entity, 'created_at'):
            entity.created_at = get_current_utc_datetime()
        if hasattr(entity, 'updated_at'):
            entity.updated_at = get_current_utc_datetime()
        
        self._storage[entity.id] = entity
        self.logger.info(f"Created {self.entity_name} with ID: {entity.id}")
        return entity
    
    def find_by_id(self, entity_id: str) -> Optional[T]:
        """Find entity by ID."""
        entity = self._storage.get(entity_id)
        if entity:
            self.logger.debug(f"Found {self.entity_name} with ID: {entity_id}")
        else:
            self.logger.debug(f"{self.entity_name} not found with ID: {entity_id}")
        return entity
    
    def find_all(self) -> List[T]:
        """Find all entities."""
        entities = list(self._storage.values())
        self.logger.debug(f"Found {len(entities)} {self.entity_name} entities")
        return entities
    
    def update(self, entity_id: str, entity: T) -> T:
        """Update an existing entity."""
        if entity_id not in self._storage:
            raise NotFoundError(f"{self.entity_name} with ID {entity_id} not found")
        
        entity.id = entity_id
        if hasattr(entity, 'updated_at'):
            entity.updated_at = get_current_utc_datetime()
        
        self._storage[entity_id] = entity
        self.logger.info(f"Updated {self.entity_name} with ID: {entity_id}")
        return entity
    
    def delete(self, entity_id: str) -> bool:
        """Delete an entity."""
        if entity_id in self._storage:
            del self._storage[entity_id]
            self.logger.info(f"Deleted {self.entity_name} with ID: {entity_id}")
            return True
        else:
            self.logger.warning(f"Attempted to delete non-existent {self.entity_name} with ID: {entity_id}")
            return False
    
    def find_by_field(self, field_name: str, value) -> List[T]:
        """Find entities by a specific field value."""
        results = []
        for entity in self._storage.values():
            if hasattr(entity, field_name) and getattr(entity, field_name) == value:
                results.append(entity)
        
        self.logger.debug(f"Found {len(results)} {self.entity_name} entities with {field_name}={value}")
        return results
    
    def find_by_predicate(self, predicate: Callable[[T], bool]) -> List[T]:
        """Find entities matching a predicate function."""
        results = [entity for entity in self._storage.values() if predicate(entity)]
        self.logger.debug(f"Found {len(results)} {self.entity_name} entities matching predicate")
        return results
    
    def count(self) -> int:
        """Count total entities."""
        return len(self._storage)
    
    def clear(self) -> None:
        """Clear all entities (useful for testing)."""
        count = len(self._storage)
        self._storage.clear()
        self.logger.info(f"Cleared {count} {self.entity_name} entities")