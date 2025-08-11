"""Base repository interface and in-memory implementation."""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
import copy

from ..utils.helpers import generate_uuid, get_current_datetime
from ..exceptions import ValidationError, NotificationServiceError


class BaseRepository(ABC):
    """Abstract base repository interface."""
    
    @abstractmethod
    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new entity."""
        pass
    
    @abstractmethod
    def find_by_id(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Find entity by ID."""
        pass
    
    @abstractmethod
    def find_all(self) -> List[Dict[str, Any]]:
        """Find all entities."""
        pass
    
    @abstractmethod
    def update(self, entity_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update entity by ID."""
        pass
    
    @abstractmethod
    def delete(self, entity_id: str) -> bool:
        """Delete entity by ID."""
        pass
    
    @abstractmethod
    def find_by_criteria(self, criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find entities matching criteria."""
        pass


class InMemoryRepository(BaseRepository):
    """In-memory repository implementation."""
    
    def __init__(self, entity_name: str = "entity"):
        """Initialize repository with entity name for error messages."""
        self.entity_name = entity_name
        self._data: Dict[str, Dict[str, Any]] = {}
        self._indexes: Dict[str, Dict[Any, List[str]]] = {}
    
    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new entity with auto-generated ID and timestamps."""
        entity_id = data.get('id') or generate_uuid()
        current_time = get_current_datetime()
        
        # Create entity with system fields
        entity = copy.deepcopy(data)
        entity.update({
            'id': entity_id,
            'created_at': current_time,
            'updated_at': current_time
        })
        
        # Set default created_by and updated_by if not provided
        if 'created_by' not in entity:
            entity['created_by'] = 'system'
        if 'updated_by' not in entity:
            entity['updated_by'] = 'system'
        
        # Store entity
        self._data[entity_id] = entity
        
        # Update indexes
        self._update_indexes(entity_id, entity)
        
        return copy.deepcopy(entity)
    
    def find_by_id(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Find entity by ID."""
        entity = self._data.get(entity_id)
        return copy.deepcopy(entity) if entity else None
    
    def find_all(self) -> List[Dict[str, Any]]:
        """Find all entities."""
        return [copy.deepcopy(entity) for entity in self._data.values()]
    
    def update(self, entity_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update entity by ID."""
        if entity_id not in self._data:
            return None
        
        # Get current entity
        entity = self._data[entity_id]
        
        # Remove from old indexes
        self._remove_from_indexes(entity_id, entity)
        
        # Apply updates
        updated_entity = copy.deepcopy(entity)
        updated_entity.update(updates)
        updated_entity['updated_at'] = get_current_datetime()
        
        # Store updated entity
        self._data[entity_id] = updated_entity
        
        # Update indexes
        self._update_indexes(entity_id, updated_entity)
        
        return copy.deepcopy(updated_entity)
    
    def delete(self, entity_id: str) -> bool:
        """Delete entity by ID."""
        if entity_id not in self._data:
            return False
        
        entity = self._data[entity_id]
        
        # Remove from indexes
        self._remove_from_indexes(entity_id, entity)
        
        # Delete entity
        del self._data[entity_id]
        
        return True
    
    def find_by_criteria(self, criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find entities matching criteria."""
        results = []
        
        for entity in self._data.values():
            if self._matches_criteria(entity, criteria):
                results.append(copy.deepcopy(entity))
        
        return results
    
    def find_by_field(self, field_name: str, field_value: Any) -> List[Dict[str, Any]]:
        """Find entities by specific field value."""
        # Use index if available
        if field_name in self._indexes and field_value in self._indexes[field_name]:
            entity_ids = self._indexes[field_name][field_value]
            return [copy.deepcopy(self._data[entity_id]) for entity_id in entity_ids if entity_id in self._data]
        
        # Fallback to full scan
        return self.find_by_criteria({field_name: field_value})
    
    def count(self) -> int:
        """Count total entities."""
        return len(self._data)
    
    def count_by_criteria(self, criteria: Dict[str, Any]) -> int:
        """Count entities matching criteria."""
        return len(self.find_by_criteria(criteria))
    
    def exists(self, entity_id: str) -> bool:
        """Check if entity exists."""
        return entity_id in self._data
    
    def clear(self) -> None:
        """Clear all data (useful for testing)."""
        self._data.clear()
        self._indexes.clear()
    
    def create_index(self, field_name: str) -> None:
        """Create an index on a field for faster lookups."""
        if field_name not in self._indexes:
            self._indexes[field_name] = {}
            
            # Build index for existing data
            for entity_id, entity in self._data.items():
                if field_name in entity:
                    field_value = entity[field_name]
                    if field_value not in self._indexes[field_name]:
                        self._indexes[field_name][field_value] = []
                    self._indexes[field_name][field_value].append(entity_id)
    
    def _matches_criteria(self, entity: Dict[str, Any], criteria: Dict[str, Any]) -> bool:
        """Check if entity matches all criteria."""
        for key, value in criteria.items():
            if key not in entity:
                return False
            
            entity_value = entity[key]
            
            # Handle different comparison types
            if isinstance(value, dict):
                # Support for operators like {'$gt': 10}, {'$in': [1, 2, 3]}
                if '$gt' in value and entity_value <= value['$gt']:
                    return False
                if '$gte' in value and entity_value < value['$gte']:
                    return False
                if '$lt' in value and entity_value >= value['$lt']:
                    return False
                if '$lte' in value and entity_value > value['$lte']:
                    return False
                if '$in' in value and entity_value not in value['$in']:
                    return False
                if '$nin' in value and entity_value in value['$nin']:
                    return False
                if '$ne' in value and entity_value == value['$ne']:
                    return False
            elif isinstance(value, list):
                # Check if entity value is in the list
                if entity_value not in value:
                    return False
            else:
                # Direct equality check
                if entity_value != value:
                    return False
        
        return True
    
    def _update_indexes(self, entity_id: str, entity: Dict[str, Any]) -> None:
        """Update indexes for an entity."""
        for field_name in self._indexes:
            if field_name in entity:
                field_value = entity[field_name]
                if field_value not in self._indexes[field_name]:
                    self._indexes[field_name][field_value] = []
                if entity_id not in self._indexes[field_name][field_value]:
                    self._indexes[field_name][field_value].append(entity_id)
    
    def _remove_from_indexes(self, entity_id: str, entity: Dict[str, Any]) -> None:
        """Remove entity from indexes."""
        for field_name in self._indexes:
            if field_name in entity:
                field_value = entity[field_name]
                if field_value in self._indexes[field_name]:
                    if entity_id in self._indexes[field_name][field_value]:
                        self._indexes[field_name][field_value].remove(entity_id)
                    # Clean up empty index entries
                    if not self._indexes[field_name][field_value]:
                        del self._indexes[field_name][field_value]
    
    def find_with_pagination(self, criteria: Dict[str, Any] = None, 
                           page: int = 1, page_size: int = 10,
                           sort_by: str = None, sort_desc: bool = False) -> Dict[str, Any]:
        """Find entities with pagination and sorting."""
        # Get all matching entities
        if criteria:
            entities = self.find_by_criteria(criteria)
        else:
            entities = self.find_all()
        
        # Sort if requested
        if sort_by:
            reverse = sort_desc
            try:
                entities.sort(key=lambda x: x.get(sort_by, ''), reverse=reverse)
            except TypeError:
                # Handle mixed types by converting to string
                entities.sort(key=lambda x: str(x.get(sort_by, '')), reverse=reverse)
        
        # Calculate pagination
        total_count = len(entities)
        start_index = (page - 1) * page_size
        end_index = start_index + page_size
        
        # Get page data
        page_data = entities[start_index:end_index]
        
        return {
            'data': page_data,
            'pagination': {
                'page': page,
                'page_size': page_size,
                'total_count': total_count,
                'total_pages': (total_count + page_size - 1) // page_size,
                'has_next': end_index < total_count,
                'has_prev': page > 1
            }
        }