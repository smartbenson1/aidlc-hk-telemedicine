"""
DynamoDB table schema for appointments.
"""

import boto3
from botocore.exceptions import ClientError
import logging

logger = logging.getLogger(__name__)


def create_appointments_table():
    """Create the appointments table in DynamoDB."""
    
    dynamodb = boto3.resource('dynamodb')
    
    table_name = 'user-management-appointments'
    
    try:
        # Check if table already exists
        table = dynamodb.Table(table_name)
        table.load()
        logger.info(f"Table {table_name} already exists")
        return table
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            # Table doesn't exist, create it
            logger.info(f"Creating table {table_name}")
            
            table = dynamodb.create_table(
                TableName=table_name,
                KeySchema=[
                    {
                        'AttributeName': 'appointment_id',
                        'KeyType': 'HASH'  # Partition key
                    }
                ],
                AttributeDefinitions=[
                    {
                        'AttributeName': 'appointment_id',
                        'AttributeType': 'S'
                    },
                    {
                        'AttributeName': 'patient_id',
                        'AttributeType': 'S'
                    },
                    {
                        'AttributeName': 'doctor_id',
                        'AttributeType': 'S'
                    },
                    {
                        'AttributeName': 'appointment_date',
                        'AttributeType': 'S'
                    }
                ],
                GlobalSecondaryIndexes=[
                    {
                        'IndexName': 'patient-appointments-index',
                        'KeySchema': [
                            {
                                'AttributeName': 'patient_id',
                                'KeyType': 'HASH'
                            },
                            {
                                'AttributeName': 'appointment_date',
                                'KeyType': 'RANGE'
                            }
                        ],
                        'Projection': {
                            'ProjectionType': 'ALL'
                        },
                        'ProvisionedThroughput': {
                            'ReadCapacityUnits': 5,
                            'WriteCapacityUnits': 5
                        }
                    },
                    {
                        'IndexName': 'doctor-appointments-index',
                        'KeySchema': [
                            {
                                'AttributeName': 'doctor_id',
                                'KeyType': 'HASH'
                            },
                            {
                                'AttributeName': 'appointment_date',
                                'KeyType': 'RANGE'
                            }
                        ],
                        'Projection': {
                            'ProjectionType': 'ALL'
                        },
                        'ProvisionedThroughput': {
                            'ReadCapacityUnits': 5,
                            'WriteCapacityUnits': 5
                        }
                    }
                ],
                ProvisionedThroughput={
                    'ReadCapacityUnits': 5,
                    'WriteCapacityUnits': 5
                }
            )
            
            # Wait for table to be created
            table.wait_until_exists()
            logger.info(f"Table {table_name} created successfully")
            return table
        else:
            logger.error(f"Error checking/creating table: {e}")
            raise


if __name__ == '__main__':
    create_appointments_table()