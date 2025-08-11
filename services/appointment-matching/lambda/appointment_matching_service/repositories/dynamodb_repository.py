"""
DynamoDB repository implementations for the Appointment Matching Service.
"""
import boto3
import json
from decimal import Decimal
from datetime import datetime
from typing import List, Optional, Dict, Any
from boto3.dynamodb.conditions import Key, Attr

from ..models.doctor import Doctor
from ..models.patient import Patient
from ..models.appointment import Appointment
from ..models.symptom_description import SymptomDescription
from ..utils.helpers import setup_logging
from ..utils.enums import UserStatus, AppointmentStatus, AppointmentType
from ..utils.exceptions import NotFoundError, ValidationError


class BaseDynamoDBRepository:
    """Base repository for DynamoDB operations."""
    
    def __init__(self, table_name: str):
        self.dynamodb = boto3.resource('dynamodb')
        self.table = self.dynamodb.Table(table_name)
        self.logger = setup_logging(f"{self.__class__.__name__}")
    
    def _serialize_item(self, item: Any) -> Dict[str, Any]:
        """Serialize item for DynamoDB storage."""
        if hasattr(item, '__dict__'):
            result = {}
            for key, value in item.__dict__.items():
                result[key] = self._serialize_value(value)
            return result
        return self._serialize_value(item)
    
    def _serialize_value(self, value):
        """Serialize individual values for DynamoDB."""
        if isinstance(value, datetime):
            return value.isoformat()
        elif isinstance(value, Decimal):
            return value  # Keep as Decimal for DynamoDB
        elif hasattr(value, 'value'):  # For enums
            return value.value
        elif isinstance(value, list):
            return [self._serialize_value(item) for item in value]
        elif isinstance(value, dict):
            return {k: self._serialize_value(v) for k, v in value.items()}
        elif hasattr(value, '__dict__'):
            return self._serialize_item(value)
        return value


class DoctorDynamoDBRepository(BaseDynamoDBRepository):
    """DynamoDB repository for Doctor entities."""
    
    def __init__(self):
        super().__init__('appointment-matching-doctors')
    
    def create(self, doctor: Doctor) -> Doctor:
        """Create a new doctor."""
        try:
            doctor.validate()
            item = self._serialize_item(doctor)
            self.table.put_item(Item=item)
            self.logger.info(f"Created doctor: {doctor.id}")
            return doctor
        except Exception as e:
            self.logger.error(f"Failed to create doctor: {e}")
            raise
    
    def find_by_id(self, doctor_id: str) -> Optional[Doctor]:
        """Find doctor by ID."""
        try:
            response = self.table.get_item(Key={'id': doctor_id})
            if 'Item' not in response:
                return None
            
            item = response['Item']
            return self._item_to_doctor(item)
        except Exception as e:
            self.logger.error(f"Failed to find doctor {doctor_id}: {e}")
            return None
    
    def find_all(self) -> List[Doctor]:
        """Find all doctors."""
        try:
            response = self.table.scan()
            doctors = []
            for item in response.get('Items', []):
                try:
                    doctor = self._item_to_doctor(item)
                    doctors.append(doctor)
                except Exception as e:
                    self.logger.warning(f"Failed to parse doctor item: {e}")
                    continue
            return doctors
        except Exception as e:
            self.logger.error(f"Failed to find all doctors: {e}")
            return []
    
    def find_active(self) -> List[Doctor]:
        """Find all active doctors."""
        try:
            response = self.table.scan(
                FilterExpression=Attr('status').eq('active')
            )
            doctors = []
            for item in response.get('Items', []):
                try:
                    doctor = self._item_to_doctor(item)
                    doctors.append(doctor)
                except Exception as e:
                    self.logger.warning(f"Failed to parse doctor item: {e}")
                    continue
            return doctors
        except Exception as e:
            self.logger.error(f"Failed to find active doctors: {e}")
            return []
    
    def update(self, doctor_id: str, doctor: Doctor) -> Doctor:
        """Update a doctor."""
        try:
            doctor.validate()
            item = self._serialize_item(doctor)
            self.table.put_item(Item=item)
            self.logger.info(f"Updated doctor: {doctor_id}")
            return doctor
        except Exception as e:
            self.logger.error(f"Failed to update doctor {doctor_id}: {e}")
            raise
    
    def delete(self, doctor_id: str) -> bool:
        """Delete a doctor."""
        try:
            self.table.delete_item(Key={'id': doctor_id})
            self.logger.info(f"Deleted doctor: {doctor_id}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to delete doctor {doctor_id}: {e}")
            return False
    
    def _item_to_doctor(self, item: Dict[str, Any]) -> Doctor:
        """Convert DynamoDB item to Doctor object."""
        return Doctor(
            id=item.get('id', ''),
            name=item.get('name', ''),
            email=item.get('email', ''),
            phone=item.get('phone', ''),
            location=item.get('location', ''),
            specialties=item.get('specialties', []),
            experience=item.get('experience', ''),
            rating=Decimal(str(item.get('rating', 0.0))),
            status=UserStatus(item.get('status', 'active')),
            created_at=datetime.fromisoformat(item['created_at']) if item.get('created_at') else None,
            updated_at=datetime.fromisoformat(item['updated_at']) if item.get('updated_at') else None,
            created_by=item.get('created_by'),
            updated_by=item.get('updated_by')
        )


class PatientDynamoDBRepository(BaseDynamoDBRepository):
    """DynamoDB repository for Patient entities."""
    
    def __init__(self):
        super().__init__('appointment-matching-patients')
    
    def create(self, patient: Patient) -> Patient:
        """Create a new patient."""
        try:
            patient.validate()
            item = self._serialize_item(patient)
            self.table.put_item(Item=item)
            self.logger.info(f"Created patient: {patient.id}")
            return patient
        except Exception as e:
            self.logger.error(f"Failed to create patient: {e}")
            raise
    
    def find_by_id(self, patient_id: str) -> Optional[Patient]:
        """Find patient by ID."""
        try:
            response = self.table.get_item(Key={'id': patient_id})
            if 'Item' not in response:
                return None
            
            item = response['Item']
            return self._item_to_patient(item)
        except Exception as e:
            self.logger.error(f"Failed to find patient {patient_id}: {e}")
            return None
    
    def find_all(self) -> List[Patient]:
        """Find all patients."""
        try:
            response = self.table.scan()
            patients = []
            for item in response.get('Items', []):
                try:
                    patient = self._item_to_patient(item)
                    patients.append(patient)
                except Exception as e:
                    self.logger.warning(f"Failed to parse patient item: {e}")
                    continue
            return patients
        except Exception as e:
            self.logger.error(f"Failed to find all patients: {e}")
            return []
    
    def update(self, patient_id: str, patient: Patient) -> Patient:
        """Update a patient."""
        try:
            patient.validate()
            item = self._serialize_item(patient)
            self.table.put_item(Item=item)
            self.logger.info(f"Updated patient: {patient_id}")
            return patient
        except Exception as e:
            self.logger.error(f"Failed to update patient {patient_id}: {e}")
            raise
    
    def delete(self, patient_id: str) -> bool:
        """Delete a patient."""
        try:
            self.table.delete_item(Key={'id': patient_id})
            self.logger.info(f"Deleted patient: {patient_id}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to delete patient {patient_id}: {e}")
            return False
    
    def _item_to_patient(self, item: Dict[str, Any]) -> Patient:
        """Convert DynamoDB item to Patient object."""
        return Patient(
            id=item.get('id', ''),
            name=item.get('name', ''),
            email=item.get('email', ''),
            phone=item.get('phone', ''),
            medical_history=item.get('medical_history', ''),
            emergency_contact_name=item.get('emergency_contact_name', ''),
            emergency_contact_phone=item.get('emergency_contact_phone', ''),
            emergency_contact_relationship=item.get('emergency_contact_relationship', ''),
            status=UserStatus(item.get('status', 'active')),
            created_at=datetime.fromisoformat(item['created_at']) if item.get('created_at') else None,
            updated_at=datetime.fromisoformat(item['updated_at']) if item.get('updated_at') else None,
            created_by=item.get('created_by'),
            updated_by=item.get('updated_by')
        )


class AppointmentDynamoDBRepository(BaseDynamoDBRepository):
    """DynamoDB repository for Appointment entities."""
    
    def __init__(self):
        super().__init__('appointment-matching-appointments')
    
    def create(self, appointment: Appointment) -> Appointment:
        """Create a new appointment."""
        try:
            appointment.validate()
            item = self._serialize_item(appointment)
            self.table.put_item(Item=item)
            self.logger.info(f"Created appointment: {appointment.id}")
            return appointment
        except Exception as e:
            self.logger.error(f"Failed to create appointment: {e}")
            raise
    
    def find_by_id(self, appointment_id: str) -> Optional[Appointment]:
        """Find appointment by ID."""
        try:
            response = self.table.get_item(Key={'id': appointment_id})
            if 'Item' not in response:
                return None
            
            item = response['Item']
            return self._item_to_appointment(item)
        except Exception as e:
            self.logger.error(f"Failed to find appointment {appointment_id}: {e}")
            return None
    
    def find_by_patient(self, patient_id: str) -> List[Appointment]:
        """Find appointments by patient ID."""
        try:
            response = self.table.scan(
                FilterExpression=Attr('patient_id').eq(patient_id)
            )
            appointments = []
            for item in response.get('Items', []):
                try:
                    appointment = self._item_to_appointment(item)
                    appointments.append(appointment)
                except Exception as e:
                    self.logger.warning(f"Failed to parse appointment item: {e}")
                    continue
            return appointments
        except Exception as e:
            self.logger.error(f"Failed to find appointments for patient {patient_id}: {e}")
            return []
    
    def find_by_doctor(self, doctor_id: str) -> List[Appointment]:
        """Find appointments by doctor ID."""
        try:
            response = self.table.scan(
                FilterExpression=Attr('doctor_id').eq(doctor_id)
            )
            appointments = []
            for item in response.get('Items', []):
                try:
                    appointment = self._item_to_appointment(item)
                    appointments.append(appointment)
                except Exception as e:
                    self.logger.warning(f"Failed to parse appointment item: {e}")
                    continue
            return appointments
        except Exception as e:
            self.logger.error(f"Failed to find appointments for doctor {doctor_id}: {e}")
            return []
    
    def find_all(self) -> List[Appointment]:
        """Find all appointments."""
        try:
            response = self.table.scan()
            appointments = []
            for item in response.get('Items', []):
                try:
                    appointment = self._item_to_appointment(item)
                    appointments.append(appointment)
                except Exception as e:
                    self.logger.warning(f"Failed to parse appointment item: {e}")
                    continue
            return appointments
        except Exception as e:
            self.logger.error(f"Failed to find all appointments: {e}")
            return []
    
    def update(self, appointment_id: str, appointment: Appointment) -> Appointment:
        """Update an appointment."""
        try:
            appointment.validate()
            item = self._serialize_item(appointment)
            self.table.put_item(Item=item)
            self.logger.info(f"Updated appointment: {appointment_id}")
            return appointment
        except Exception as e:
            self.logger.error(f"Failed to update appointment {appointment_id}: {e}")
            raise
    
    def delete(self, appointment_id: str) -> bool:
        """Delete an appointment."""
        try:
            self.table.delete_item(Key={'id': appointment_id})
            self.logger.info(f"Deleted appointment: {appointment_id}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to delete appointment {appointment_id}: {e}")
            return False
    
    def _item_to_appointment(self, item: Dict[str, Any]) -> Appointment:
        """Convert DynamoDB item to Appointment object."""
        return Appointment(
            id=item.get('id', ''),
            patient_id=item.get('patient_id', ''),
            doctor_id=item.get('doctor_id', ''),
            availability_id=item.get('availability_id', ''),
            datetime=datetime.fromisoformat(item['datetime']) if item.get('datetime') else None,
            appointment_type=AppointmentType(item.get('appointment_type', 'in_person')),
            symptoms=item.get('symptoms', ''),
            status=AppointmentStatus(item.get('status', 'scheduled')),
            reschedule_reason=item.get('reschedule_reason'),
            reschedule_count=item.get('reschedule_count', 0),
            created_at=datetime.fromisoformat(item['created_at']) if item.get('created_at') else None,
            updated_at=datetime.fromisoformat(item['updated_at']) if item.get('updated_at') else None,
            created_by=item.get('created_by'),
            updated_by=item.get('updated_by')
        )


class SymptomDescriptionDynamoDBRepository(BaseDynamoDBRepository):
    """DynamoDB repository for SymptomDescription entities."""
    
    def __init__(self):
        super().__init__('appointment-matching-symptoms')
    
    def create(self, symptom_desc: SymptomDescription) -> SymptomDescription:
        """Create a new symptom description."""
        try:
            symptom_desc.validate()
            item = self._serialize_item(symptom_desc)
            self.table.put_item(Item=item)
            self.logger.info(f"Created symptom description: {symptom_desc.id}")
            return symptom_desc
        except Exception as e:
            self.logger.error(f"Failed to create symptom description: {e}")
            raise
    
    def find_by_id(self, symptom_id: str) -> Optional[SymptomDescription]:
        """Find symptom description by ID."""
        try:
            response = self.table.get_item(Key={'id': symptom_id})
            if 'Item' not in response:
                return None
            
            item = response['Item']
            return self._item_to_symptom_description(item)
        except Exception as e:
            self.logger.error(f"Failed to find symptom description {symptom_id}: {e}")
            return None
    
    def find_by_patient(self, patient_id: str) -> List[SymptomDescription]:
        """Find symptom descriptions by patient ID."""
        try:
            response = self.table.scan(
                FilterExpression=Attr('patient_id').eq(patient_id)
            )
            symptoms = []
            for item in response.get('Items', []):
                try:
                    symptom = self._item_to_symptom_description(item)
                    symptoms.append(symptom)
                except Exception as e:
                    self.logger.warning(f"Failed to parse symptom item: {e}")
                    continue
            return symptoms
        except Exception as e:
            self.logger.error(f"Failed to find symptoms for patient {patient_id}: {e}")
            return []
    
    def find_all(self) -> List[SymptomDescription]:
        """Find all symptom descriptions."""
        try:
            response = self.table.scan()
            symptoms = []
            for item in response.get('Items', []):
                try:
                    symptom = self._item_to_symptom_description(item)
                    symptoms.append(symptom)
                except Exception as e:
                    self.logger.warning(f"Failed to parse symptom item: {e}")
                    continue
            return symptoms
        except Exception as e:
            self.logger.error(f"Failed to find all symptom descriptions: {e}")
            return []
    
    def update(self, symptom_id: str, symptom_desc: SymptomDescription) -> SymptomDescription:
        """Update a symptom description."""
        try:
            symptom_desc.validate()
            item = self._serialize_item(symptom_desc)
            self.table.put_item(Item=item)
            self.logger.info(f"Updated symptom description: {symptom_id}")
            return symptom_desc
        except Exception as e:
            self.logger.error(f"Failed to update symptom description {symptom_id}: {e}")
            raise
    
    def delete(self, symptom_id: str) -> bool:
        """Delete a symptom description."""
        try:
            self.table.delete_item(Key={'id': symptom_id})
            self.logger.info(f"Deleted symptom description: {symptom_id}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to delete symptom description {symptom_id}: {e}")
            return False
    
    def _item_to_symptom_description(self, item: Dict[str, Any]) -> SymptomDescription:
        """Convert DynamoDB item to SymptomDescription object."""
        return SymptomDescription(
            id=item.get('id', ''),
            patient_id=item.get('patient_id', ''),
            symptoms_text=item.get('symptoms_text', ''),
            parsed_keywords=item.get('parsed_keywords', []),
            confidence_score=Decimal(str(item.get('confidence_score', 0.0))),
            matched_specialties=item.get('matched_specialties', []),
            analysis_timestamp=datetime.fromisoformat(item['analysis_timestamp']) if item.get('analysis_timestamp') else None,
            created_at=datetime.fromisoformat(item['created_at']) if item.get('created_at') else None,
            updated_at=datetime.fromisoformat(item['updated_at']) if item.get('updated_at') else None,
            created_by=item.get('created_by'),
            updated_by=item.get('updated_by')
        )