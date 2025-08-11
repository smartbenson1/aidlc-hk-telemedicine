"""
Base DynamoDB repository with common operations.
"""

import json
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any, Type, TypeVar
from uuid import UUID
from datetime import datetime
from botocore.exceptions import ClientError

from .dynamodb_client import get_dynamodb_client
from ..utils.logging_utils import get_logger
from ..utils.exceptions import RepositoryError, NotFoundError

logger = get_logger(__name__)

T = TypeVar('T')


class BaseDynamoDBRepository(ABC):
    """Base repository class for DynamoDB operations."""
    
    def __init__(self):
        """Initialize the repository."""
        self.client = get_dynamodb_client()
        self.table = self.client.table
    
    @abstractmethod
    def _to_dynamodb_item(self, entity: T) -> Dict[str, Any]:
        """Convert entity to DynamoDB item format."""
        pass
    
    @abstractmethod
    def _from_dynamodb_item(self, item: Dict[str, Any]) -> T:
        """Convert DynamoDB item to entity format."""
        pass
    
    @abstractmethod
    def _get_partition_key(self, entity_id: UUID) -> str:
        """Get partition key for the entity."""
        pass
    
    @abstractmethod
    def _get_sort_key(self, entity: Optional[T] = None) -> str:
        """Get sort key for the entity."""
        pass
    
    def create(self, entity: T) -> T:
        """Create a new entity."""
        try:
            item = self._to_dynamodb_item(entity)
            
            # Add timestamps
            now = datetime.utcnow().isoformat()
            item['created_at'] = now
            item['updated_at'] = now
            
            # Use condition expression to prevent overwrites
            self.table.put_item(
                Item=item,
                ConditionExpression='attribute_not_exists(PK)'
            )
            
            logger.info(f"Created entity with PK: {item['PK']}")
            return entity
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                raise RepositoryError(f"Entity already exists")
            else:
                logger.error(f"Failed to create entity: {str(e)}")
                raise RepositoryError(f"Failed to create entity: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error creating entity: {str(e)}")
            raise RepositoryError(f"Failed to create entity: {str(e)}")
    
    def find_by_id(self, entity_id: UUID) -> Optional[T]:
        """Find entity by ID."""
        try:
            pk = self._get_partition_key(entity_id)
            sk = self._get_sort_key()
            
            response = self.table.get_item(
                Key={
                    'PK': pk,
                    'SK': sk
                }
            )
            
            if 'Item' in response:
                return self._from_dynamodb_item(response['Item'])
            else:
                return None
                
        except Exception as e:
            logger.error(f"Failed to find entity by ID {entity_id}: {str(e)}")
            raise RepositoryError(f"Failed to find entity: {str(e)}")
    
    def update(self, entity: T) -> T:
        """Update an existing entity."""
        try:
            item = self._to_dynamodb_item(entity)
            
            # Update timestamp
            item['updated_at'] = datetime.utcnow().isoformat()
            
            # Use condition expression to ensure entity exists
            self.table.put_item(
                Item=item,
                ConditionExpression='attribute_exists(PK)'
            )
            
            logger.info(f"Updated entity with PK: {item['PK']}")
            return entity
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                raise NotFoundError(f"Entity not found for update")
            else:
                logger.error(f"Failed to update entity: {str(e)}")
                raise RepositoryError(f"Failed to update entity: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error updating entity: {str(e)}")
            raise RepositoryError(f"Failed to update entity: {str(e)}")
    
    def delete(self, entity_id: UUID) -> bool:
        """Delete an entity by ID."""
        try:
            pk = self._get_partition_key(entity_id)
            sk = self._get_sort_key()
            
            response = self.table.delete_item(
                Key={
                    'PK': pk,
                    'SK': sk
                },
                ConditionExpression='attribute_exists(PK)',
                ReturnValues='ALL_OLD'
            )
            
            deleted = 'Attributes' in response
            if deleted:
                logger.info(f"Deleted entity with PK: {pk}")
            
            return deleted
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                return False  # Entity didn't exist
            else:
                logger.error(f"Failed to delete entity: {str(e)}")
                raise RepositoryError(f"Failed to delete entity: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error deleting entity: {str(e)}")
            raise RepositoryError(f"Failed to delete entity: {str(e)}")
    
    def find_all(self) -> List[T]:
        """Find all entities of this type."""
        try:
            # This is expensive for large datasets - consider pagination
            response = self.table.scan(
                FilterExpression='attribute_exists(entity_type) AND entity_type = :entity_type',
                ExpressionAttributeValues={
                    ':entity_type': self._get_entity_type()
                }
            )
            
            entities = []
            for item in response.get('Items', []):
                try:
                    entity = self._from_dynamodb_item(item)
                    entities.append(entity)
                except Exception as e:
                    logger.warning(f"Failed to convert item to entity: {str(e)}")
                    continue
            
            logger.info(f"Found {len(entities)} entities of type {self._get_entity_type()}")
            return entities
            
        except Exception as e:
            logger.error(f"Failed to find all entities: {str(e)}")
            raise RepositoryError(f"Failed to find entities: {str(e)}")
    
    def query_by_gsi(self, index_name: str, partition_key: str, sort_key_prefix: Optional[str] = None) -> List[T]:
        """Query entities using a Global Secondary Index."""
        try:
            query_params = {
                'IndexName': index_name,
                'KeyConditionExpression': 'GSI1PK = :pk' if index_name == 'GSI1' else f'{index_name}PK = :pk',
                'ExpressionAttributeValues': {
                    ':pk': partition_key
                }
            }
            
            # Add sort key condition if provided
            if sort_key_prefix:
                if index_name == 'GSI1':
                    query_params['KeyConditionExpression'] += ' AND begins_with(GSI1SK, :sk)'
                else:
                    query_params['KeyConditionExpression'] += f' AND begins_with({index_name}SK, :sk)'
                query_params['ExpressionAttributeValues'][':sk'] = sort_key_prefix
            
            response = self.table.query(**query_params)
            
            entities = []
            for item in response.get('Items', []):
                try:
                    entity = self._from_dynamodb_item(item)
                    entities.append(entity)
                except Exception as e:
                    logger.warning(f"Failed to convert item to entity: {str(e)}")
                    continue
            
            return entities
            
        except Exception as e:
            logger.error(f"Failed to query GSI {index_name}: {str(e)}")
            raise RepositoryError(f"Failed to query index: {str(e)}")
    
    @abstractmethod
    def _get_entity_type(self) -> str:
        """Get the entity type string for filtering."""
        pass
    
    def _serialize_for_dynamodb(self, obj: Any) -> Any:
        """Serialize complex objects for DynamoDB storage."""
        if isinstance(obj, UUID):
            return str(obj)
        elif isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, list):
            return [self._serialize_for_dynamodb(item) for item in obj]
        elif isinstance(obj, dict):
            return {key: self._serialize_for_dynamodb(value) for key, value in obj.items()}
        elif hasattr(obj, '__dict__'):
            # Handle dataclass or custom objects
            return {key: self._serialize_for_dynamodb(value) for key, value in obj.__dict__.items()}
        else:
            return obj
    
    def _deserialize_from_dynamodb(self, obj: Any, target_type: Type = None) -> Any:
        """Deserialize objects from DynamoDB storage."""
        if target_type == UUID and isinstance(obj, str):
            return UUID(obj)
        elif target_type == datetime and isinstance(obj, str):
            return datetime.fromisoformat(obj)
        elif isinstance(obj, list):
            return [self._deserialize_from_dynamodb(item) for item in obj]
        elif isinstance(obj, dict):
            return {key: self._deserialize_from_dynamodb(value) for key, value in obj.items()}
        else:
            return obj