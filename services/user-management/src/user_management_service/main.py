"""
Main entry point and example usage for the User Management Service.
"""

import logging
from datetime import datetime, timedelta
from uuid import uuid4

# Import all the components
from .repositories.doctor_repository import DoctorRepository
from .repositories.patient_repository import PatientRepository
from .repositories.specialty_repository import MedicalSpecialtyRepository
from .repositories.availability_repository import DoctorAvailabilityRepository
from .repositories.session_repository import UserSessionRepository

from .services.registration_service import UserRegistrationService
from .services.profile_service import ProfileManagementService
from .services.availability_service import AvailabilityManagementService
from .services.session_service import UserSessionManager

from .integrations.email_service import EmailServiceIntegration
from .integrations.admin_service import AdministrationServiceIntegration
from .integrations.appointment_service import AppointmentServiceIntegration

from .requests.registration_requests import DoctorRegistrationRequest, PatientRegistrationRequest
from .requests.profile_update_requests import DoctorProfileUpdateRequest, PatientProfileUpdateRequest
from .requests.availability_requests import TimeSlotRequest

from .models.medical_specialty import MedicalSpecialty
from .utils.enums import AppointmentType, UserStatus
from .utils.config import get_config
from .utils.logging_utils import setup_logging

logger = logging.getLogger(__name__)


class UserManagementServiceDemo:
    """Demo class showing how to use the User Management Service."""
    
    def __init__(self):
        """Initialize the service with all dependencies."""
        # Load configuration
        self.config = get_config()
        
        # Setup logging
        setup_logging(
            log_level=self.config.logging.log_level,
            log_file=self.config.logging.log_file
        )
        
        # Initialize repositories
        self.doctor_repository = DoctorRepository()
        self.patient_repository = PatientRepository()
        self.specialty_repository = MedicalSpecialtyRepository()
        self.availability_repository = DoctorAvailabilityRepository()
        self.session_repository = UserSessionRepository()
        
        # Initialize integrations
        self.email_service = EmailServiceIntegration(
            smtp_server=self.config.email.smtp_server,
            smtp_port=self.config.email.smtp_port,
            sender_email=self.config.email.sender_email,
            smtp_username=self.config.email.smtp_username,
            smtp_password=self.config.email.smtp_password
        )
        
        self.admin_service = AdministrationServiceIntegration(
            base_url=self.config.integrations.admin_service_url,
            api_key=self.config.integrations.admin_service_api_key,
            timeout_seconds=self.config.integrations.request_timeout_seconds
        )
        
        self.appointment_service = AppointmentServiceIntegration(
            base_url=self.config.integrations.appointment_service_url,
            api_key=self.config.integrations.appointment_service_api_key,
            timeout_seconds=self.config.integrations.request_timeout_seconds
        )
        
        # Initialize services
        self.registration_service = UserRegistrationService(
            self.doctor_repository,
            self.patient_repository,
            self.specialty_repository,
            self.email_service
        )
        
        self.profile_service = ProfileManagementService(
            self.doctor_repository,
            self.patient_repository,
            self.specialty_repository,
            self.session_repository
        )
        
        self.availability_service = AvailabilityManagementService(
            self.doctor_repository,
            self.availability_repository,
            self.specialty_repository,
            self.session_repository,
            self.appointment_service
        )
        
        self.session_manager = UserSessionManager(
            self.session_repository,
            self.doctor_repository,
            self.patient_repository
        )
    
    def setup_sample_data(self):
        """Set up sample data for testing."""
        logger.info("Setting up sample data...")
        
        # Check if specialties already exist
        existing_specialties = self.specialty_repository.find_all()
        if existing_specialties:
            logger.info(f"Found {len(existing_specialties)} existing specialties, skipping sample data creation")
            return existing_specialties
        
        # Create comprehensive medical specialties only if none exist
        specialties = [
            MedicalSpecialty(name="General Practice", description="Primary healthcare and family medicine"),
            MedicalSpecialty(name="Internal Medicine", description="Adult internal medicine and general medical care"),
            MedicalSpecialty(name="Cardiology", description="Heart and cardiovascular system"),
            MedicalSpecialty(name="Dermatology", description="Skin, hair, and nail conditions"),
            MedicalSpecialty(name="Emergency Medicine", description="Emergency and urgent medical care"),
            MedicalSpecialty(name="Anesthesiology", description="Anesthesia and perioperative care"),
            MedicalSpecialty(name="Radiology", description="Medical imaging and diagnostic radiology"),
            MedicalSpecialty(name="Pathology", description="Laboratory medicine and disease diagnosis"),
            MedicalSpecialty(name="Psychiatry", description="Mental health and psychiatric disorders"),
            MedicalSpecialty(name="Obstetrics and Gynecology", description="Women's reproductive health and childbirth"),
            MedicalSpecialty(name="Ophthalmology", description="Eye and vision care"),
            MedicalSpecialty(name="Otolaryngology", description="Ear, nose, and throat disorders"),
            MedicalSpecialty(name="Urology", description="Urinary system and male reproductive health"),
            MedicalSpecialty(name="Gastroenterology", description="Digestive system disorders"),
            MedicalSpecialty(name="Pulmonology", description="Respiratory system and lung diseases"),
            MedicalSpecialty(name="Endocrinology", description="Hormonal and metabolic disorders"),
            MedicalSpecialty(name="Rheumatology", description="Autoimmune and joint diseases"),
            MedicalSpecialty(name="Hematology", description="Blood disorders and diseases"),
            MedicalSpecialty(name="Oncology", description="Cancer diagnosis and treatment"),
            MedicalSpecialty(name="Nephrology", description="Kidney diseases and disorders"),
            MedicalSpecialty(name="Infectious Disease", description="Infectious diseases and immunology"),
            MedicalSpecialty(name="Allergy and Immunology", description="Allergic reactions and immune system disorders"),
            MedicalSpecialty(name="Physical Medicine", description="Rehabilitation and physical therapy medicine"),
            MedicalSpecialty(name="Plastic Surgery", description="Reconstructive and cosmetic surgery"),
            MedicalSpecialty(name="Orthopedic Surgery", description="Surgical treatment of musculoskeletal conditions"),
            MedicalSpecialty(name="Neurosurgery", description="Surgical treatment of nervous system disorders"),
            MedicalSpecialty(name="Cardiac Surgery", description="Heart and cardiovascular surgery"),
            MedicalSpecialty(name="Thoracic Surgery", description="Chest and lung surgery"),
            MedicalSpecialty(name="Vascular Surgery", description="Blood vessel and circulation surgery"),
            MedicalSpecialty(name="General Surgery", description="General surgical procedures"),
            MedicalSpecialty(name="Pediatric Surgery", description="Surgical care for children"),
            MedicalSpecialty(name="Trauma Surgery", description="Emergency surgical care for injuries"),
            MedicalSpecialty(name="Pediatrics", description="Medical care of infants, children, and adolescents"),
            MedicalSpecialty(name="Orthopedics", description="Musculoskeletal system"),
            MedicalSpecialty(name="Neurology", description="Nervous system disorders"),
            MedicalSpecialty(name="Sports Medicine", description="Athletic injuries and performance medicine"),
            MedicalSpecialty(name="Occupational Medicine", description="Workplace health and safety"),
            MedicalSpecialty(name="Preventive Medicine", description="Disease prevention and public health"),
            MedicalSpecialty(name="Geriatrics", description="Healthcare for elderly patients"),
            MedicalSpecialty(name="Palliative Care", description="Comfort care and end-of-life medicine"),
            MedicalSpecialty(name="Pain Management", description="Chronic pain treatment and management"),
            MedicalSpecialty(name="Sleep Medicine", description="Sleep disorders and sleep health"),
            MedicalSpecialty(name="Addiction Medicine", description="Substance abuse and addiction treatment"),
            MedicalSpecialty(name="Nuclear Medicine", description="Nuclear imaging and radiopharmaceuticals"),
            MedicalSpecialty(name="Interventional Radiology", description="Image-guided minimally invasive procedures")
        ]
        
        for specialty in specialties:
            self.specialty_repository.create(specialty)
        
        logger.info(f"Created {len(specialties)} sample specialties")
        return specialties
    
    def demo_doctor_registration(self, specialties):
        """Demonstrate doctor registration."""
        logger.info("=== Doctor Registration Demo ===")
        
        # Create doctor registration request
        doctor_request = DoctorRegistrationRequest(
            name="Dr. John Smith",
            email="john.smith@example.com",
            phone="(555) 123-4567",
            location="123 Medical Center Dr, New York, NY 10001",
            specialties=[specialties[0].id, specialties[1].id],  # Cardiology and Dermatology
            experience="10 years of experience in cardiology and general practice. Board certified in internal medicine."
        )
        
        # Register doctor
        result = self.registration_service.register_doctor(doctor_request)
        
        if result.success:
            logger.info(f"Doctor registered successfully: {result.data.user_id}")
            return result.data.user_id
        else:
            logger.error(f"Doctor registration failed: {result.error_message}")
            return None
    
    def demo_patient_registration(self):
        """Demonstrate patient registration."""
        logger.info("=== Patient Registration Demo ===")
        
        # Create patient registration request
        patient_request = PatientRegistrationRequest(
            name="Jane Doe",
            email="jane.doe@example.com",
            phone="(555) 987-6543",
            medical_history="No known allergies. Previous surgery: appendectomy in 2020.",
            emergency_contact_name="John Doe",
            emergency_contact_phone="(555) 987-6544",
            emergency_contact_relationship="spouse"
        )
        
        # Register patient
        result = self.registration_service.register_patient(patient_request)
        
        if result.success:
            logger.info(f"Patient registered successfully: {result.data.user_id}")
            return result.data.user_id
        else:
            logger.error(f"Patient registration failed: {result.error_message}")
            return None
    
    def demo_session_management(self, doctor_id, patient_id):
        """Demonstrate session management."""
        logger.info("=== Session Management Demo ===")
        
        # Create doctor session
        doctor_session_result = self.session_manager.create_session(
            doctor_id, "doctor", "192.168.1.100", "Mozilla/5.0 (Demo Browser)"
        )
        
        if doctor_session_result.success:
            doctor_session_id = doctor_session_result.data.session_id
            logger.info(f"Doctor session created: {doctor_session_id}")
            
            # Validate session
            validation_result = self.session_manager.validate_session(doctor_session_id)
            if validation_result.success:
                logger.info(f"Session validation successful: {validation_result.data.is_valid}")
            
            return doctor_session_id
        else:
            logger.error(f"Doctor session creation failed: {doctor_session_result.error_message}")
            return None
    
    def demo_profile_management(self, doctor_id, session_id):
        """Demonstrate profile management."""
        logger.info("=== Profile Management Demo ===")
        
        # Get doctor profile
        profile_result = self.profile_service.get_doctor_profile(doctor_id, session_id)
        if profile_result.success:
            logger.info(f"Retrieved doctor profile: {profile_result.data.name}")
        
        # Update doctor profile
        update_request = DoctorProfileUpdateRequest(
            phone="(555) 123-4568",  # Updated phone number
            experience="11 years of experience in cardiology and general practice. Board certified in internal medicine."
        )
        
        update_result = self.profile_service.update_doctor_profile(doctor_id, update_request, session_id)
        if update_result.success:
            logger.info(f"Profile updated successfully. Changed fields: {update_result.data.updated_fields}")
        else:
            logger.error(f"Profile update failed: {update_result.error_message}")
    
    def demo_availability_management(self, doctor_id, session_id, specialties):
        """Demonstrate availability management."""
        logger.info("=== Availability Management Demo ===")
        
        # Create time slot request
        tomorrow = datetime.utcnow() + timedelta(days=1)
        slot_time = tomorrow.replace(hour=14, minute=0, second=0, microsecond=0)  # 2 PM tomorrow
        
        slot_request = TimeSlotRequest(
            datetime=slot_time,
            appointment_type=AppointmentType.IN_PERSON,
            specialty_id=specialties[0].id  # Cardiology
        )
        
        # Add time slot
        slot_result = self.availability_service.add_time_slot(doctor_id, slot_request, session_id)
        if slot_result.success:
            logger.info(f"Time slot added successfully: {slot_result.data.availability_id}")
            return slot_result.data.availability_id
        else:
            logger.error(f"Time slot creation failed: {slot_result.error_message}")
            return None
    
    def demo_statistics(self):
        """Demonstrate statistics gathering."""
        logger.info("=== Statistics Demo ===")
        
        # Get registration statistics
        reg_stats = self.registration_service.get_registration_statistics()
        if reg_stats.success:
            logger.info(f"Registration statistics: {reg_stats.data}")
        
        # Get session statistics
        session_stats = self.session_manager.get_session_statistics()
        if session_stats.success:
            logger.info(f"Session statistics: {session_stats.data}")
        
        # Get availability statistics
        avail_stats = self.availability_service.get_availability_statistics()
        if avail_stats.success:
            logger.info(f"Availability statistics: {avail_stats.data}")
    
    def run_full_demo(self):
        """Run the complete demo."""
        logger.info("Starting User Management Service Demo")
        
        try:
            # Setup sample data
            specialties = self.setup_sample_data()
            
            # Demo registrations
            doctor_id = self.demo_doctor_registration(specialties)
            patient_id = self.demo_patient_registration()
            
            if doctor_id and patient_id:
                # Demo session management
                session_id = self.demo_session_management(doctor_id, patient_id)
                
                if session_id:
                    # Demo profile management
                    self.demo_profile_management(doctor_id, session_id)
                    
                    # Demo availability management
                    self.demo_availability_management(doctor_id, session_id, specialties)
            
            # Demo statistics
            self.demo_statistics()
            
            logger.info("Demo completed successfully!")
            
        except Exception as e:
            logger.error(f"Demo failed with error: {str(e)}")
            raise


def main():
    """Main function to run the demo."""
    demo = UserManagementServiceDemo()
    demo.run_full_demo()


if __name__ == "__main__":
    main()