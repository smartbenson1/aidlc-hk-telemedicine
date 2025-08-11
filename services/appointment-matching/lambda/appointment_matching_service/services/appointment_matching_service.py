"""
Main Appointment Matching Service orchestrator class.
"""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Optional, Dict, Any

from ..models.doctor import Doctor
from ..models.patient import Patient
from ..models.appointment import Appointment
from ..models.symptom_description import SymptomDescription
from ..models.doctor_recommendation import DoctorRecommendation
from ..models.doctor_availability import DoctorAvailability
from ..models.appointment_booking_event import AppointmentBookingEvent
from ..models.analysis_results import AnalysisResult, SpecialtyMatch

from ..repositories.dynamodb_repository import (
    DoctorDynamoDBRepository,
    PatientDynamoDBRepository, 
    AppointmentDynamoDBRepository,
    SymptomDescriptionDynamoDBRepository
)

from ..services.symptom_analyzer import SymptomAnalyzer
from ..services.specialty_matcher import SpecialtyMatcher

from ..utils.helpers import generate_uuid, get_current_utc_datetime, setup_logging
from ..utils.exceptions import (
    AppointmentMatchingServiceError, ValidationError, NotFoundError, 
    BusinessRuleError, BookingError
)
from ..utils.enums import AppointmentStatus, UserStatus, AvailabilityStatus


class AppointmentMatchingService:
    """Main orchestrator service for appointment matching functionality."""
    
    def __init__(self):
        # Initialize DynamoDB repositories
        self.doctor_repository = DoctorDynamoDBRepository()
        self.patient_repository = PatientDynamoDBRepository()
        self.appointment_repository = AppointmentDynamoDBRepository()
        self.symptom_repository = SymptomDescriptionDynamoDBRepository()
        
        # Initialize services
        self.symptom_analyzer = SymptomAnalyzer()
        self.specialty_matcher = SpecialtyMatcher()
        
        self.logger = setup_logging("AppointmentMatchingService")
        self.logger.info("Appointment Matching Service initialized")
    
    # US-P003: Describe Symptoms
    def describe_symptoms(self, patient_id: str, symptoms_text: str) -> SymptomDescription:
        """
        Process patient symptom description and analyze using NLP.
        
        User Story: US-P003 - As a patient, I want to describe my symptoms 
        in free text so that the system can match me with appropriate doctors.
        """
        try:
            self.logger.info(f"Processing symptom description for patient: {patient_id}")
            
            # Validate input
            if not patient_id or not symptoms_text:
                raise ValidationError("Patient ID and symptoms text are required")
            
            # Create symptom description
            symptom_desc = SymptomDescription(
                patient_id=patient_id,
                symptoms_text=symptoms_text.strip()
            )
            
            # Validate the symptom description
            symptom_desc.validate()
            
            # Analyze symptoms using NLP
            analysis_result = self.symptom_analyzer.analyze_symptoms(symptoms_text)
            
            # Update symptom description with analysis results
            specialty_matches = self.specialty_matcher.match_specialties(analysis_result.keywords)
            matched_specialty_ids = [match.specialty_id for match in specialty_matches[:5]]
            
            symptom_desc.update_analysis_results(
                keywords=analysis_result.keywords,
                specialties=matched_specialty_ids,
                confidence=analysis_result.confidence_score
            )
            
            # Save to repository
            saved_symptom_desc = self.symptom_repository.create(symptom_desc)
            
            self.logger.info(f"Symptom description created with ID: {saved_symptom_desc.id}")
            return saved_symptom_desc
            
        except Exception as e:
            self.logger.error(f"Failed to process symptom description: {e}")
            raise AppointmentMatchingServiceError(f"Failed to describe symptoms: {e}")
    
    # US-P004: View Doctor Recommendations
    def get_doctor_recommendations(self, symptom_description_id: str) -> DoctorRecommendation:
        """
        Get doctor recommendations based on symptom analysis.
        
        User Story: US-P004 - As a patient, I want to see recommended doctors 
        based on my symptoms so that I can choose the most suitable one.
        """
        try:
            self.logger.info(f"Getting doctor recommendations for symptom: {symptom_description_id}")
            
            # Get symptom description
            symptom_desc = self.symptom_repository.find_by_id(symptom_description_id)
            if not symptom_desc:
                raise NotFoundError(f"Symptom description not found: {symptom_description_id}")
            
            if not symptom_desc.is_analyzed():
                raise BusinessRuleError("Symptoms must be analyzed before getting recommendations")
            
            # Match specialties
            specialty_matches = self.specialty_matcher.match_specialties(symptom_desc.parsed_keywords)
            
            # Find doctors for matched specialties
            candidate_doctors = []
            for match in specialty_matches[:3]:  # Top 3 specialties
                # In real implementation, we'd use actual specialty IDs
                # For demo, we'll get all active doctors
                doctors = self.doctor_repository.find_active()
                candidate_doctors.extend(doctors)
            
            # Remove duplicates and limit to active doctors
            unique_doctors = list({d.id: d for d in candidate_doctors if d.is_active()}.values())
            
            # Rank doctors by rating and availability (simplified)
            ranked_doctors = self._rank_doctors_simple(unique_doctors)
            
            # Get top 3 recommendations
            top_doctors = ranked_doctors[:3]
            
            # Create recommendation
            recommendation = DoctorRecommendation(
                symptom_description_id=symptom_description_id,
                patient_id=symptom_desc.patient_id,
                recommended_doctors=[d.id for d in top_doctors],
                match_scores=[Decimal('0.9'), Decimal('0.8'), Decimal('0.7')][:len(top_doctors)],
                available_slots=[get_current_utc_datetime() + timedelta(days=i+1) for i in range(len(top_doctors))],
                algorithm_version="1.0"
            )
            
            recommendation.validate()
            
            self.logger.info(f"Generated {len(top_doctors)} doctor recommendations")
            return recommendation
            
        except Exception as e:
            self.logger.error(f"Failed to get doctor recommendations: {e}")
            raise AppointmentMatchingServiceError(f"Failed to get recommendations: {e}")
    
    # US-P006: Book Appointment
    def book_appointment(self, patient_id: str, doctor_id: str, 
                        appointment_datetime: datetime, symptoms: str,
                        appointment_type: str = "in_person") -> Appointment:
        """
        Book an appointment with a selected doctor.
        
        User Story: US-P006 - As a patient, I want to book an appointment 
        with a selected doctor so that I can receive medical care.
        """
        try:
            self.logger.info(f"Booking appointment for patient {patient_id} with doctor {doctor_id}")
            
            # Validate input
            if not all([patient_id, doctor_id, appointment_datetime, symptoms]):
                raise ValidationError("All appointment details are required")
            
            # Check if doctor exists and is active
            doctor = self.doctor_repository.find_by_id(doctor_id)
            if not doctor or not doctor.is_active():
                raise NotFoundError("Doctor not found or not active")
            
            # Validate booking window (30 days in advance, minimum 1 hour)
            current_time = get_current_utc_datetime()
            if appointment_datetime <= current_time + timedelta(hours=1):
                raise BookingError("Appointment must be at least 1 hour in advance")
            
            if appointment_datetime > current_time + timedelta(days=30):
                raise BookingError("Appointment cannot be more than 30 days in advance")
            
            # Check for conflicts (simplified - in real implementation, check availability)
            existing_appointments = self.appointment_repository.find_by_doctor(doctor_id)
            for apt in existing_appointments:
                if (apt.datetime and apt.is_scheduled() and 
                    abs((apt.datetime - appointment_datetime).total_seconds()) < 3600):
                    raise BookingError("Time slot is not available")
            
            # Create appointment
            appointment = Appointment(
                patient_id=patient_id,
                doctor_id=doctor_id,
                availability_id=generate_uuid(),  # In real implementation, link to actual availability
                datetime=appointment_datetime,
                symptoms=symptoms,
                status=AppointmentStatus.SCHEDULED
            )
            
            appointment.validate()
            
            # Save appointment
            saved_appointment = self.appointment_repository.create(appointment)
            
            # Create booking event
            booking_event = AppointmentBookingEvent(
                appointment_id=saved_appointment.id,
                patient_id=patient_id,
                doctor_id=doctor_id,
                datetime=appointment_datetime,
                symptoms=symptoms
            )
            
            self.logger.info(f"Appointment booked successfully: {saved_appointment.id}")
            return saved_appointment
            
        except Exception as e:
            self.logger.error(f"Failed to book appointment: {e}")
            raise BookingError(f"Failed to book appointment: {e}")
    
    # US-P007: View My Appointments
    def get_patient_appointments(self, patient_id: str) -> List[Appointment]:
        """
        Get all appointments for a patient.
        
        User Story: US-P007 - As a patient, I want to view my scheduled 
        appointments so that I can keep track of my medical care.
        """
        try:
            self.logger.info(f"Getting appointments for patient: {patient_id}")
            
            if not patient_id:
                raise ValidationError("Patient ID is required")
            
            appointments = self.appointment_repository.find_by_patient(patient_id)
            
            # Sort by datetime (upcoming first)
            current_time = get_current_utc_datetime()
            upcoming = [apt for apt in appointments if apt.datetime and apt.datetime > current_time]
            past = [apt for apt in appointments if apt.datetime and apt.datetime <= current_time]
            
            upcoming.sort(key=lambda x: x.datetime or datetime.min)
            past.sort(key=lambda x: x.datetime or datetime.min, reverse=True)
            
            sorted_appointments = upcoming + past
            
            self.logger.info(f"Found {len(sorted_appointments)} appointments for patient")
            return sorted_appointments
            
        except Exception as e:
            self.logger.error(f"Failed to get patient appointments: {e}")
            raise AppointmentMatchingServiceError(f"Failed to get appointments: {e}")
    
    # US-P008: Reschedule Appointment
    def reschedule_appointment(self, appointment_id: str, new_datetime: datetime, 
                             reason: str) -> Appointment:
        """
        Reschedule an existing appointment.
        
        User Story: US-P008 - As a patient, I want to reschedule my appointment 
        so that I can adjust to changes in my schedule.
        """
        try:
            self.logger.info(f"Rescheduling appointment: {appointment_id}")
            
            # Validate input
            if not all([appointment_id, new_datetime, reason]):
                raise ValidationError("Appointment ID, new datetime, and reason are required")
            
            # Get existing appointment
            appointment = self.appointment_repository.find_by_id(appointment_id)
            if not appointment:
                raise NotFoundError(f"Appointment not found: {appointment_id}")
            
            # Check if appointment can be rescheduled
            if not appointment.can_reschedule():
                raise BusinessRuleError("Appointment cannot be rescheduled")
            
            # Validate new datetime
            current_time = get_current_utc_datetime()
            if new_datetime <= current_time + timedelta(hours=24):
                raise BusinessRuleError("Reschedule must be at least 24 hours before appointment")
            
            # Reschedule the appointment
            appointment.reschedule(new_datetime, reason)
            
            # Update in repository
            updated_appointment = self.appointment_repository.update(appointment_id, appointment)
            
            self.logger.info(f"Appointment rescheduled successfully: {appointment_id}")
            return updated_appointment
            
        except Exception as e:
            self.logger.error(f"Failed to reschedule appointment: {e}")
            raise BusinessRuleError(f"Failed to reschedule appointment: {e}")
    
    # US-D005: Doctor View Appointments
    def get_doctor_appointments(self, doctor_id: str) -> List[Appointment]:
        """
        Get all appointments for a doctor.
        
        User Story: US-D005 - As a doctor, I want to view my scheduled 
        appointments so that I can prepare for patient consultations.
        """
        try:
            self.logger.info(f"Getting appointments for doctor: {doctor_id}")
            
            if not doctor_id:
                raise ValidationError("Doctor ID is required")
            
            appointments = self.appointment_repository.find_by_doctor(doctor_id)
            
            # Sort by datetime (upcoming first)
            current_time = get_current_utc_datetime()
            upcoming = [apt for apt in appointments if apt.datetime and apt.datetime > current_time]
            past = [apt for apt in appointments if apt.datetime and apt.datetime <= current_time]
            
            upcoming.sort(key=lambda x: x.datetime or datetime.min)
            past.sort(key=lambda x: x.datetime or datetime.min, reverse=True)
            
            sorted_appointments = upcoming + past
            
            self.logger.info(f"Found {len(sorted_appointments)} appointments for doctor")
            return sorted_appointments
            
        except Exception as e:
            self.logger.error(f"Failed to get doctor appointments: {e}")
            raise AppointmentMatchingServiceError(f"Failed to get appointments: {e}")
    
    def _rank_doctors_simple(self, doctors: List[Doctor]) -> List[Doctor]:
        """Simple doctor ranking by rating (highest first)."""
        return sorted(doctors, key=lambda d: d.rating, reverse=True)
    
    def get_service_stats(self) -> Dict[str, Any]:
        """Get service statistics."""
        return {
            'total_doctors': self.doctor_repository.count(),
            'total_appointments': self.appointment_repository.count(),
            'total_symptoms': self.symptom_repository.count(),
            'service_status': 'active',
            'last_updated': get_current_utc_datetime().isoformat()
        }