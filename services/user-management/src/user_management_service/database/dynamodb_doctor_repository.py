"""
DynamoDB implementation of Doctor repository.
"""

from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime

from .base_dynamodb_repository import BaseDynamoDBRepository
from ..models.doctor import Doctor
from ..utils.enums import UserStatus
from ..utils.logging_utils import get_logger

logger = get_logger(__name__)


class DynamoDBDoctorRepository(BaseDynamoDBRepository):
    """DynamoDB implementation of doctor repository."""
    
    def _to_dynamodb_item(self, doctor: Doctor) -> Dict[str, Any]:
        """Convert Doctor entity to DynamoDB item format for CDK-created table."""
        return {
            'id': str(doctor.id),
            'user_type': 'doctor',  # For user-type-index
            'name': doctor.name,
            'email': doctor.email,  # For email-index
            'phone': doctor.phone,
            'location': doctor.location,
            'specialties': [str(s) for s in doctor.specialties],
            'experience': doctor.experience,
            'rating': doctor.rating,  # Keep as Decimal
            'status': doctor.status.value if hasattr(doctor.status, 'value') else str(doctor.status),
            'created_at': doctor.created_at.isoformat() if hasattr(doctor.created_at, 'isoformat') else str(doctor.created_at),
            'updated_at': doctor.updated_at.isoformat() if hasattr(doctor.updated_at, 'isoformat') else str(doctor.updated_at)
        }
    
    def _from_dynamodb_item(self, item: Dict[str, Any]) -> Doctor:
        """Convert DynamoDB item to Doctor entity."""
        from decimal import Decimal
        from datetime import datetime
        
        # Handle created_at and updated_at
        created_at = item.get('created_at')
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
        elif created_at is None:
            created_at = datetime.utcnow()
        
        updated_at = item.get('updated_at')
        if isinstance(updated_at, str):
            updated_at = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
        elif updated_at is None:
            updated_at = datetime.utcnow()
        
        return Doctor(
            id=item['id'],  # Keep as string for now
            name=item['name'],
            email=item['email'],
            phone=item['phone'],
            location=item['location'],
            specialties=item.get('specialties', []),  # Keep as strings
            experience=item['experience'],
            rating=Decimal(str(item.get('rating', 4.5))),
            status=UserStatus(item.get('status', 'ACTIVE')),
            created_at=created_at,
            updated_at=updated_at
        )
    
    def _get_partition_key(self, doctor_id: UUID) -> str:
        """Get partition key for doctor."""
        return f'DOCTOR#{doctor_id}'
    
    def _get_sort_key(self, doctor: Optional[Doctor] = None) -> str:
        """Get sort key for doctor."""
        return 'PROFILE'
    
    def _get_entity_type(self) -> str:
        """Get entity type for filtering."""
        return 'doctor'
    
    def find_by_email(self, email: str) -> Optional[Doctor]:
        """Find doctor by email address."""
        try:
            # Use the email-index created by CDK instead of GSI1
            response = self.table.query(
                IndexName='email-index',
                KeyConditionExpression='email = :email',
                ExpressionAttributeValues={':email': email}
            )
            doctors = [self._item_to_doctor(item) for item in response['Items']]
            
            return doctors[0] if doctors else None
            
        except Exception as e:
            logger.error(f"Failed to find doctor by email {email}: {str(e)}")
            raise
    
    def find_by_specialty(self, specialty_id: UUID) -> List[Doctor]:
        """Find doctors by specialty."""
        try:
            # For this query, we need to scan since specialties is a list attribute
            # In a production system, you might want to create a separate GSI
            # or denormalize the data for better query performance
            
            response = self.table.scan(
                FilterExpression='contains(specialties, :specialty_id) AND entity_type = :entity_type',
                ExpressionAttributeValues={
                    ':specialty_id': str(specialty_id),
                    ':entity_type': 'doctor'
                }
            )
            
            doctors = []
            for item in response.get('Items', []):
                try:
                    doctor = self._from_dynamodb_item(item)
                    doctors.append(doctor)
                except Exception as e:
                    logger.warning(f"Failed to convert item to doctor: {str(e)}")
                    continue
            
            logger.info(f"Found {len(doctors)} doctors with specialty {specialty_id}")
            return doctors
            
        except Exception as e:
            logger.error(f"Failed to find doctors by specialty {specialty_id}: {str(e)}")
            raise
    
    def find_active_doctors(self) -> List[Doctor]:
        """Find all active doctors."""
        try:
            response = self.table.scan(
                FilterExpression='entity_type = :entity_type AND #status = :status',
                ExpressionAttributeNames={
                    '#status': 'status'  # 'status' is a reserved word in DynamoDB
                },
                ExpressionAttributeValues={
                    ':entity_type': 'doctor',
                    ':status': UserStatus.ACTIVE.value
                }
            )
            
            doctors = []
            for item in response.get('Items', []):
                try:
                    doctor = self._from_dynamodb_item(item)
                    doctors.append(doctor)
                except Exception as e:
                    logger.warning(f"Failed to convert item to doctor: {str(e)}")
                    continue
            
            logger.info(f"Found {len(doctors)} active doctors")
            return doctors
            
        except Exception as e:
            logger.error(f"Failed to find active doctors: {str(e)}")
            raise
    
    def create_with_email_check(self, doctor: Doctor) -> Doctor:
        """Create doctor with email uniqueness check using direct DynamoDB operations."""
        try:
            # Check if email already exists using the email-index
            response = self.table.query(
                IndexName='email-index',
                KeyConditionExpression='email = :email',
                ExpressionAttributeValues={':email': doctor.email}
            )
            
            if response['Items']:
                from ..utils.exceptions import DuplicateError
                raise DuplicateError(f"Doctor with email {doctor.email} already exists")
            
            # Create the doctor item directly
            doctor_item = self._to_dynamodb_item(doctor)
            
            # Save to DynamoDB using put_item
            self.table.put_item(Item=doctor_item)
            
            logger.info(f"Doctor created successfully: {doctor.id}")
            return doctor
            
        except Exception as e:
            logger.error(f"Failed to create doctor with email check: {str(e)}")
            raise
    
    def email_exists(self, email: str) -> bool:
        """Check if email already exists."""
        try:
            existing_doctor = self.find_by_email(email)
            return existing_doctor is not None
        except Exception as e:
            logger.error(f"Failed to check email existence: {str(e)}")
            return False
    
    def update_rating(self, doctor_id: UUID, new_rating: float) -> bool:
        """Update doctor's rating."""
        try:
            pk = self._get_partition_key(doctor_id)
            sk = self._get_sort_key()
            
            response = self.table.update_item(
                Key={
                    'PK': pk,
                    'SK': sk
                },
                UpdateExpression='SET rating = :rating, updated_at = :updated_at',
                ExpressionAttributeValues={
                    ':rating': new_rating,
                    ':updated_at': datetime.utcnow().isoformat()
                },
                ConditionExpression='attribute_exists(PK)',
                ReturnValues='UPDATED_NEW'
            )
            
            logger.info(f"Updated rating for doctor {doctor_id} to {new_rating}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update rating for doctor {doctor_id}: {str(e)}")
            return False
    
    def get_doctor_count(self) -> int:
        """Get total count of doctors."""
        try:
            response = self.table.scan(
                FilterExpression='entity_type = :entity_type',
                ExpressionAttributeValues={
                    ':entity_type': 'doctor'
                },
                Select='COUNT'
            )
            
            return response.get('Count', 0)
            
        except Exception as e:
            logger.error(f"Failed to get doctor count: {str(e)}")
            return 0
    
    def get_active_doctor_count(self) -> int:
        """Get count of active doctors."""
        try:
            response = self.table.scan(
                FilterExpression='entity_type = :entity_type AND #status = :status',
                ExpressionAttributeNames={
                    '#status': 'status'
                },
                ExpressionAttributeValues={
                    ':entity_type': 'doctor',
                    ':status': UserStatus.ACTIVE.value
                },
                Select='COUNT'
            )
            
            return response.get('Count', 0)
            
        except Exception as e:
            logger.error(f"Failed to get active doctor count: {str(e)}")
            return 0
    
    def get_all_active_doctors(self, limit: int = 50, specialty: str = None) -> List[Doctor]:
        """Get all active doctors with optional specialty filter."""
        try:
            filter_expression = 'entity_type = :entity_type AND #status = :status'
            expression_attribute_names = {'#status': 'status'}
            expression_attribute_values = {
                ':entity_type': 'doctor',
                ':status': UserStatus.ACTIVE.value
            }
            
            # Add specialty filter if provided
            if specialty:
                filter_expression += ' AND contains(specialties, :specialty)'
                expression_attribute_values[':specialty'] = specialty
            
            response = self.table.scan(
                FilterExpression=filter_expression,
                ExpressionAttributeNames=expression_attribute_names,
                ExpressionAttributeValues=expression_attribute_values,
                Limit=limit
            )
            
            doctors = []
            for item in response.get('Items', []):
                try:
                    doctor = self._from_dynamodb_item(item)
                    doctors.append(doctor)
                except Exception as e:
                    logger.warning(f"Failed to convert item to doctor: {str(e)}")
                    continue
            
            logger.info(f"Found {len(doctors)} active doctors")
            return doctors
            
        except Exception as e:
            logger.error(f"Failed to get all active doctors: {str(e)}")
            return []
    
    def search_doctors(self, specialty: str = None, location: str = None, limit: int = 20) -> List[Doctor]:
        """Search doctors by various criteria."""
        try:
            filter_expression = 'entity_type = :entity_type AND #status = :status'
            expression_attribute_names = {'#status': 'status'}
            expression_attribute_values = {
                ':entity_type': 'doctor',
                ':status': UserStatus.ACTIVE.value
            }
            
            # Add specialty filter if provided
            if specialty:
                filter_expression += ' AND contains(specialties, :specialty)'
                expression_attribute_values[':specialty'] = specialty
            
            # Add location filter if provided
            if location:
                filter_expression += ' AND contains(#location, :location)'
                expression_attribute_names['#location'] = 'location'
                expression_attribute_values[':location'] = location
            
            response = self.table.scan(
                FilterExpression=filter_expression,
                ExpressionAttributeNames=expression_attribute_names,
                ExpressionAttributeValues=expression_attribute_values,
                Limit=limit
            )
            
            doctors = []
            for item in response.get('Items', []):
                try:
                    doctor = self._from_dynamodb_item(item)
                    doctors.append(doctor)
                except Exception as e:
                    logger.warning(f"Failed to convert item to doctor: {str(e)}")
                    continue
            
            logger.info(f"Found {len(doctors)} doctors matching search criteria")
            return doctors
            
        except Exception as e:
            logger.error(f"Failed to search doctors: {str(e)}")
            return []
    
    def get_by_id(self, doctor_id: str) -> Optional[Doctor]:
        """Get doctor by ID."""
        try:
            # Handle both UUID and string IDs
            if isinstance(doctor_id, str) and not doctor_id.startswith('DOCTOR#'):
                pk = f'DOCTOR#{doctor_id}'
            else:
                pk = str(doctor_id)
            
            sk = self._get_sort_key()
            
            response = self.table.get_item(
                Key={
                    'PK': pk,
                    'SK': sk
                }
            )
            
            item = response.get('Item')
            if not item:
                return None
            
            return self._from_dynamodb_item(item)
            
        except Exception as e:
            logger.error(f"Failed to get doctor by ID {doctor_id}: {str(e)}")
            return None