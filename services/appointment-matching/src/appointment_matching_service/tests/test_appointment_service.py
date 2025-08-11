"""
Unit tests for the Appointment Matching Service.
"""

import unittest
from datetime import datetime, timedelta
from decimal import Decimal

from appointment_matching_service.services.appointment_matching_service import AppointmentMatchingService
from appointment_matching_service.models.doctor import Doctor
from appointment_matching_service.models.patient import Patient
from appointment_matching_service.utils.exceptions import ValidationError, BookingError, NotFoundError


class TestAppointmentMatchingService(unittest.TestCase):
    """Test cases for the main appointment matching service."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.service = AppointmentMatchingService()
        
        # Create test doctor
        self.doctor = Doctor(
            name="Dr. Test Smith",
            email="test.smith@hospital.com",
            phone="+1-555-0123",
            location="Test City, NY",
            specialties=["cardiology"],
            experience="Test experience",
            rating=Decimal('4.5')
        )
        self.saved_doctor = self.service.doctor_repository.create(self.doctor)
        
        # Create test patient
        self.patient = Patient(
            name="Test Patient",
            email="test.patient@email.com",
            phone="+1-555-0456",
            emergency_contact_name="Test Contact",
            emergency_contact_phone="+1-555-0789",
            emergency_contact_relationship="Spouse"
        )
        self.saved_patient = self.service.patient_repository.create(self.patient)
    
    def test_describe_symptoms_success(self):
        """Test successful symptom description."""
        symptoms_text = "I have chest pain and shortness of breath"
        
        symptom_desc = self.service.describe_symptoms(
            patient_id=self.saved_patient.id,
            symptoms_text=symptoms_text
        )
        
        self.assertIsNotNone(symptom_desc.id)
        self.assertEqual(symptom_desc.patient_id, self.saved_patient.id)
        self.assertEqual(symptom_desc.symptoms_text, symptoms_text)
        self.assertTrue(symptom_desc.is_analyzed())
        self.assertGreater(len(symptom_desc.parsed_keywords), 0)
    
    def test_describe_symptoms_validation_error(self):
        """Test symptom description with invalid input."""
        with self.assertRaises(ValidationError):
            self.service.describe_symptoms(
                patient_id="",
                symptoms_text="test symptoms"
            )
        
        with self.assertRaises(ValidationError):
            self.service.describe_symptoms(
                patient_id=self.saved_patient.id,
                symptoms_text=""
            )
    
    def test_get_doctor_recommendations_success(self):
        """Test successful doctor recommendations."""
        # First describe symptoms
        symptom_desc = self.service.describe_symptoms(
            patient_id=self.saved_patient.id,
            symptoms_text="chest pain and heart problems"
        )
        
        # Get recommendations
        recommendations = self.service.get_doctor_recommendations(symptom_desc.id)
        
        self.assertIsNotNone(recommendations.id)
        self.assertEqual(recommendations.patient_id, self.saved_patient.id)
        self.assertEqual(recommendations.symptom_description_id, symptom_desc.id)
        self.assertTrue(recommendations.has_recommendations())
    
    def test_get_doctor_recommendations_not_found(self):
        """Test doctor recommendations with invalid symptom ID."""
        with self.assertRaises(NotFoundError):
            self.service.get_doctor_recommendations("invalid-id")
    
    def test_book_appointment_success(self):
        """Test successful appointment booking."""
        appointment_time = datetime.utcnow() + timedelta(days=1)
        symptoms = "Test symptoms for appointment"
        
        appointment = self.service.book_appointment(
            patient_id=self.saved_patient.id,
            doctor_id=self.saved_doctor.id,
            appointment_datetime=appointment_time,
            symptoms=symptoms
        )
        
        self.assertIsNotNone(appointment.id)
        self.assertEqual(appointment.patient_id, self.saved_patient.id)
        self.assertEqual(appointment.doctor_id, self.saved_doctor.id)
        self.assertEqual(appointment.symptoms, symptoms)
        self.assertTrue(appointment.is_scheduled())
    
    def test_book_appointment_validation_errors(self):
        """Test appointment booking validation errors."""
        # Test booking too far in advance
        far_future = datetime.utcnow() + timedelta(days=35)
        with self.assertRaises(BookingError):
            self.service.book_appointment(
                patient_id=self.saved_patient.id,
                doctor_id=self.saved_doctor.id,
                appointment_datetime=far_future,
                symptoms="test symptoms"
            )
        
        # Test booking in the past
        past_time = datetime.utcnow() - timedelta(hours=1)
        with self.assertRaises(BookingError):
            self.service.book_appointment(
                patient_id=self.saved_patient.id,
                doctor_id=self.saved_doctor.id,
                appointment_datetime=past_time,
                symptoms="test symptoms"
            )
        
        # Test with invalid doctor
        with self.assertRaises(NotFoundError):
            self.service.book_appointment(
                patient_id=self.saved_patient.id,
                doctor_id="invalid-doctor-id",
                appointment_datetime=datetime.utcnow() + timedelta(days=1),
                symptoms="test symptoms"
            )
    
    def test_get_patient_appointments(self):
        """Test getting patient appointments."""
        # Book an appointment first
        appointment_time = datetime.utcnow() + timedelta(days=1)
        appointment = self.service.book_appointment(
            patient_id=self.saved_patient.id,
            doctor_id=self.saved_doctor.id,
            appointment_datetime=appointment_time,
            symptoms="test symptoms"
        )
        
        # Get patient appointments
        appointments = self.service.get_patient_appointments(self.saved_patient.id)
        
        self.assertEqual(len(appointments), 1)
        self.assertEqual(appointments[0].id, appointment.id)
    
    def test_get_doctor_appointments(self):
        """Test getting doctor appointments."""
        # Book an appointment first
        appointment_time = datetime.utcnow() + timedelta(days=1)
        appointment = self.service.book_appointment(
            patient_id=self.saved_patient.id,
            doctor_id=self.saved_doctor.id,
            appointment_datetime=appointment_time,
            symptoms="test symptoms"
        )
        
        # Get doctor appointments
        appointments = self.service.get_doctor_appointments(self.saved_doctor.id)
        
        self.assertEqual(len(appointments), 1)
        self.assertEqual(appointments[0].id, appointment.id)
    
    def test_reschedule_appointment_success(self):
        """Test successful appointment rescheduling."""
        # Book an appointment first
        appointment_time = datetime.utcnow() + timedelta(days=2)
        appointment = self.service.book_appointment(
            patient_id=self.saved_patient.id,
            doctor_id=self.saved_doctor.id,
            appointment_datetime=appointment_time,
            symptoms="test symptoms"
        )
        
        # Reschedule the appointment
        new_time = appointment_time + timedelta(days=1)
        reason = "Schedule conflict"
        
        rescheduled = self.service.reschedule_appointment(
            appointment_id=appointment.id,
            new_datetime=new_time,
            reason=reason
        )
        
        self.assertEqual(rescheduled.datetime, new_time)
        self.assertEqual(rescheduled.reschedule_reason, reason)
        self.assertEqual(rescheduled.reschedule_count, 1)
        self.assertTrue(rescheduled.is_rescheduled())
    
    def test_service_stats(self):
        """Test service statistics."""
        stats = self.service.get_service_stats()
        
        self.assertIn('total_doctors', stats)
        self.assertIn('total_appointments', stats)
        self.assertIn('total_symptoms', stats)
        self.assertIn('service_status', stats)
        self.assertEqual(stats['service_status'], 'active')
        self.assertGreaterEqual(stats['total_doctors'], 1)


class TestDoctorModel(unittest.TestCase):
    """Test cases for the Doctor model."""
    
    def test_doctor_creation_and_validation(self):
        """Test doctor creation and validation."""
        doctor = Doctor(
            name="Dr. Test",
            email="test@hospital.com",
            phone="+1-555-0123",
            location="Test City",
            specialties=["cardiology"],
            experience="Test experience",
            rating=Decimal('4.5')
        )
        
        self.assertTrue(doctor.validate())
        self.assertTrue(doctor.is_active())
        self.assertEqual(doctor.rating, Decimal('4.5'))
    
    def test_doctor_validation_errors(self):
        """Test doctor validation errors."""
        # Test missing required fields
        doctor = Doctor()
        with self.assertRaises(ValidationError):
            doctor.validate()
        
        # Test invalid email
        doctor = Doctor(
            name="Dr. Test",
            email="invalid-email",
            phone="+1-555-0123",
            location="Test City",
            specialties=["cardiology"],
            experience="Test experience"
        )
        with self.assertRaises(ValidationError):
            doctor.validate()


class TestPatientModel(unittest.TestCase):
    """Test cases for the Patient model."""
    
    def test_patient_creation_and_validation(self):
        """Test patient creation and validation."""
        patient = Patient(
            name="Test Patient",
            email="test@email.com",
            phone="+1-555-0123",
            emergency_contact_name="Emergency Contact",
            emergency_contact_phone="+1-555-0456",
            emergency_contact_relationship="Spouse"
        )
        
        self.assertTrue(patient.validate())
        self.assertTrue(patient.is_active())
    
    def test_patient_validation_errors(self):
        """Test patient validation errors."""
        # Test missing emergency contact
        patient = Patient(
            name="Test Patient",
            email="test@email.com",
            phone="+1-555-0123"
        )
        with self.assertRaises(ValidationError):
            patient.validate()


if __name__ == '__main__':
    unittest.main()