"""
DynamoDB client configuration and utilities.
"""

import boto3
import os
import logging
from typing import Optional, Dict, Any
from botocore.exceptions import ClientError, NoCredentialsError

from ..utils.logging_utils import get_logger

logger = get_logger(__name__)


class DynamoDBClient:
    """DynamoDB client wrapper with configuration and error handling."""
    
    def __init__(self, table_name: Optional[str] = None, region_name: Optional[str] = None):
        """Initialize DynamoDB client."""
        self.table_name = table_name or os.getenv('DYNAMODB_TABLE_NAME', 'user-management-users')
        self.region_name = region_name or os.getenv('AWS_REGION', 'us-east-1')
        
        # Initialize clients
        self._dynamodb_resource = None
        self._dynamodb_client = None
        self._table = None
        
        logger.info(f"Initializing DynamoDB client for table: {self.table_name}")
    
    @property
    def dynamodb_resource(self):
        """Get DynamoDB resource (lazy initialization)."""
        if self._dynamodb_resource is None:
            try:
                # Use endpoint URL for Lambda environment
                self._dynamodb_resource = boto3.resource(
                    'dynamodb',
                    region_name=self.region_name,
                    endpoint_url=f'https://dynamodb.{self.region_name}.amazonaws.com'
                )
                logger.info(f"DynamoDB resource initialized for region: {self.region_name}")
            except NoCredentialsError:
                logger.error("AWS credentials not found")
                raise
            except Exception as e:
                logger.error(f"Failed to initialize DynamoDB resource: {str(e)}")
                raise
        
        return self._dynamodb_resource
    
    @property
    def dynamodb_client(self):
        """Get DynamoDB client (lazy initialization)."""
        if self._dynamodb_client is None:
            try:
                # Use endpoint URL for Lambda environment
                self._dynamodb_client = boto3.client(
                    'dynamodb',
                    region_name=self.region_name,
                    endpoint_url=f'https://dynamodb.{self.region_name}.amazonaws.com'
                )
                logger.info(f"DynamoDB client initialized for region: {self.region_name}")
            except NoCredentialsError:
                logger.error("AWS credentials not found")
                raise
            except Exception as e:
                logger.error(f"Failed to initialize DynamoDB client: {str(e)}")
                raise
        
        return self._dynamodb_client
    
    @property
    def table(self):
        """Get DynamoDB table (lazy initialization)."""
        if self._table is None:
            try:
                self._table = self.dynamodb_resource.Table(self.table_name)
                logger.info(f"DynamoDB table reference created: {self.table_name}")
            except Exception as e:
                logger.error(f"Failed to get table reference: {str(e)}")
                raise
        
        return self._table
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check on DynamoDB connection."""
        try:
            # Try to describe the table
            response = self.table.meta.client.describe_table(TableName=self.table_name)
            table_status = response['Table']['TableStatus']
            
            return {
                'status': 'healthy' if table_status == 'ACTIVE' else 'unhealthy',
                'table_name': self.table_name,
                'table_status': table_status,
                'region': self.region_name
            }
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'ResourceNotFoundException':
                return {
                    'status': 'unhealthy',
                    'error': f'Table {self.table_name} not found',
                    'region': self.region_name
                }
            else:
                return {
                    'status': 'unhealthy',
                    'error': f'DynamoDB error: {error_code}',
                    'region': self.region_name
                }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'region': self.region_name
            }
    
    def create_table_if_not_exists(self) -> bool:
        """Create the DynamoDB table if it doesn't exist."""
        try:
            # Check if table exists
            self.table.load()
            logger.info(f"Table {self.table_name} already exists")
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                logger.info(f"Table {self.table_name} not found, creating...")
                return self._create_table()
            else:
                logger.error(f"Error checking table existence: {str(e)}")
                raise
    
    def _create_table(self) -> bool:
        """Create the DynamoDB table with the required schema."""
        try:
            table = self.dynamodb_resource.create_table(
                TableName=self.table_name,
                KeySchema=[
                    {
                        'AttributeName': 'PK',
                        'KeyType': 'HASH'  # Partition key
                    },
                    {
                        'AttributeName': 'SK',
                        'KeyType': 'RANGE'  # Sort key
                    }
                ],
                AttributeDefinitions=[
                    {
                        'AttributeName': 'PK',
                        'AttributeType': 'S'
                    },
                    {
                        'AttributeName': 'SK',
                        'AttributeType': 'S'
                    },
                    {
                        'AttributeName': 'GSI1PK',
                        'AttributeType': 'S'
                    },
                    {
                        'AttributeName': 'GSI1SK',
                        'AttributeType': 'S'
                    },
                    {
                        'AttributeName': 'GSI2PK',
                        'AttributeType': 'S'
                    },
                    {
                        'AttributeName': 'GSI2SK',
                        'AttributeType': 'S'
                    },
                    {
                        'AttributeName': 'GSI3PK',
                        'AttributeType': 'S'
                    },
                    {
                        'AttributeName': 'GSI3SK',
                        'AttributeType': 'S'
                    }
                ],
                GlobalSecondaryIndexes=[
                    {
                        'IndexName': 'GSI1',
                        'KeySchema': [
                            {
                                'AttributeName': 'GSI1PK',
                                'KeyType': 'HASH'
                            },
                            {
                                'AttributeName': 'GSI1SK',
                                'KeyType': 'RANGE'
                            }
                        ],
                        'Projection': {
                            'ProjectionType': 'ALL'
                        },
                        'BillingMode': 'PAY_PER_REQUEST'
                    },
                    {
                        'IndexName': 'GSI2',
                        'KeySchema': [
                            {
                                'AttributeName': 'GSI2PK',
                                'KeyType': 'HASH'
                            },
                            {
                                'AttributeName': 'GSI2SK',
                                'KeyType': 'RANGE'
                            }
                        ],
                        'Projection': {
                            'ProjectionType': 'ALL'
                        },
                        'BillingMode': 'PAY_PER_REQUEST'
                    },
                    {
                        'IndexName': 'GSI3',
                        'KeySchema': [
                            {
                                'AttributeName': 'GSI3PK',
                                'KeyType': 'HASH'
                            },
                            {
                                'AttributeName': 'GSI3SK',
                                'KeyType': 'RANGE'
                            }
                        ],
                        'Projection': {
                            'ProjectionType': 'ALL'
                        },
                        'BillingMode': 'PAY_PER_REQUEST'
                    }
                ],
                BillingMode='PAY_PER_REQUEST'
            )
            
            # Wait for table to be created
            table.wait_until_exists()
            logger.info(f"Table {self.table_name} created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create table: {str(e)}")
            raise


# Global DynamoDB client instance
_dynamodb_client = None


def get_dynamodb_client() -> DynamoDBClient:
    """Get the global DynamoDB client instance."""
    global _dynamodb_client
    if _dynamodb_client is None:
        _dynamodb_client = DynamoDBClient()
    return _dynamodb_client


def initialize_dynamodb() -> bool:
    """Initialize DynamoDB connection and create table if needed."""
    try:
        client = get_dynamodb_client()
        return client.create_table_if_not_exists()
    except Exception as e:
        logger.error(f"Failed to initialize DynamoDB: {str(e)}")
        return False