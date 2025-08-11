"""
Service Container for User Management Service with DynamoDB repositories.
"""

import logging
import os
from typing import Optional

# Import DynamoDB repositories
from .database.dynamodb_doctor_repository import DynamoDBDoctorRepository
from .database.dynamodb_client import get_dynamodb_client

# Import in-memory repositories as fallback
from .repositories.doctor_repository import DoctorRepository
from .repositories.patient_repository import PatientRepository
from .repositories.specialty_repository import MedicalSpecialtyRepository
from .repositories.availability_repository import DoctorAvailabilityRepository
from .repositories.session_repository import UserSessionRepository

# Import services
from .services.registration_service import UserRegistrationService
from .services.profile_service import ProfileManagementService
from .services.availability_service import AvailabilityManagementService
from .services.session_service import UserSessionManager

# Import integrations
from .integrations.email_service import EmailServiceIntegration
from .integrations.admin_service import AdministrationServiceIntegration
from .integrations.appointment_service import AppointmentServiceIntegration

from .utils.config import get_config
from .utils.logging_utils import setup_logging, get_logger

logger = get_logger(__name__)


class UserManagementServiceContainer:
    """Service container that uses DynamoDB repositories for production."""
    
    def __init__(self, use_dynamodb: bool = True):
        """
        Initialize the service container.
        
        Args:
            use_dynamodb: Whether to use DynamoDB repositories (True for production)
        """
        self.use_dynamodb = use_dynamodb
        self._initialized = False
        
        # Load configuration
        self.config = get_config()
        
        # Setup logging
        setup_logging(
            log_level=self.config.logging.log_level,
            log_file=self.config.logging.log_file
        )
        
        # Initialize repositories
        self._init_repositories()
        
        # Initialize integrations
        self._init_integrations()
        
        # Initialize services
        self._init_services()
        
        self._initialized = True
        logger.info(f"Service container initialized (DynamoDB: {self.use_dynamodb})")
    
    def _init_repositories(self):
        """Initialize repositories based on configuration."""
        if self.use_dynamodb:
            # Use DynamoDB repositories for production
            logger.info("Initializing DynamoDB repositories")
            
            # Initialize DynamoDB client
            self.dynamodb_client = get_dynamodb_client()
            
            # Initialize DynamoDB repositories
            self.doctor_repository = DynamoDBDoctorRepository()
            
            # For now, use in-memory repositories for other entities
            # TODO: Implement DynamoDB versions of these repositories
            self.patient_repository = PatientRepository()
            self.specialty_repository = MedicalSpecialtyRepository()
            self.availability_repository = DoctorAvailabilityRepository()
            self.session_repository = UserSessionRepository()
            
        else:
            # Use in-memory repositories for development/testing
            logger.info("Initializing in-memory repositories")
            
            self.doctor_repository = DoctorRepository()
            self.patient_repository = PatientRepository()
            self.specialty_repository = MedicalSpecialtyRepository()
            self.availability_repository = DoctorAvailabilityRepository()
            self.session_repository = UserSessionRepository()
    
    def _init_integrations(self):
        """Initialize external service integrations."""
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
    
    def _init_services(self):
        """Initialize business services."""
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
        """Set up sample data for testing (only for development)."""
        if not self.use_dynamodb:
            logger.info("Setting up sample data for development environment")
            # Only set up sample data for in-memory repositories
            from .main import UserManagementServiceDemo
            demo = UserManagementServiceDemo()
            return demo.setup_sample_data()
        else:
            logger.info("Skipping sample data setup for production environment")
            return []
    
    @property
    def is_initialized(self) -> bool:
        """Check if the service container is initialized."""
        return self._initialized


def create_service_container() -> UserManagementServiceContainer:
    """
    Factory function to create the appropriate service container.
    
    Returns:
        UserManagementServiceContainer: Configured service container
    """
    # Determine if we should use DynamoDB based on environment
    environment = os.getenv("ENVIRONMENT", "production").lower()
    use_dynamodb = environment == "production"
    
    # Override with explicit environment variable if set
    if os.getenv("USE_DYNAMODB"):
        use_dynamodb = os.getenv("USE_DYNAMODB").lower() in ("true", "1", "yes")
    
    logger.info(f"Creating service container (environment: {environment}, use_dynamodb: {use_dynamodb})")
    
    return UserManagementServiceContainer(use_dynamodb=use_dynamodb)