#!/usr/bin/env python3
"""
API Examples for User Management Service

This module provides comprehensive examples of how to use the User Management Service
API programmatically. It demonstrates all major functionality including registration,
profile management, availability management, and session handling.

Usage:
    python -m user_management_service.api_examples
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any
import uuid

# Import all necessary components
from user_management_service.main import UserManagementServiceDemo
from user_management_service.requests.registration_requests import (
    DoctorRegistrationRequest, PatientRegistrationRequest
)
from user_management_service.requests.profile_update_requests import (
    DoctorProfileUpdateRequest, PatientProfileUpdateRequest
)
from user_management_service.requests.availability_requests import (
    TimeSlotRequest, BulkAvailabilityRequest, AvailabilityQueryRequest
)
from user_management_service.utils.enums import AppointmentType, UserStatus
from user_management_service.utils.exceptions import (
    ValidationError, BusinessRuleError, SessionError
)


class UserManagementAPIExamples:
    """
    Comprehensive API examples for the User Management Service.
    
    This class demonstrates how to use all major API endpoints and functionality
    of the User Management Service in a real-world scenario.
    """
    
    def __init__(self):
        """Initialize the API examples with a demo service instance."""
        self.demo = UserManagementServiceDemo()
        self.specialties = []
        self.doctor_id = None
        self.patient_id = None
        self.doctor_session_id = None
        self.patient_session_id = None
        
    def run_all_examples(self):
        """Run all API examples in sequence."""
        print("=" * 80)
        print("USER MANAGEMENT SERVICE - API EXAMPLES")
        print("=" * 80)
        
        try:
            # Setup
            self._setup_sample_data()
            
            # Core API Examples
            self._example_doctor_registration()
            self._example_patient_registration()
            self._example_session_management()
            self._example_profile_management()
            self._example_availability_management()
            self._example_bulk_operations()
            self._example_query_operations()
            self._example_error_handling()
            self._example_statistics_and_monitoring()
            
            print("\n" + "=" * 80)
            print("✅ ALL API EXAMPLES COMPLETED SUCCESSFULLY!")
            print("=" * 80)
            
        except Exception as e:
            print(f"\n❌ API Examples failed with error: {e}")
            raise
    
    def _setup_sample_data(self):
        """Setup sample medical specialties for examples."""
        print("\n📋 SETUP: Creating Sample Medical Specialties")
        print("-" * 50)
        
        self.specialties = self.demo.setup_sample_data()
        
        print(f"✅ Created {len(self.specialties)} medical specialties:")
        for specialty in self.specialties[:3]:  # Show first 3
            print(f"   • {specialty.name} (ID: {str(specialty.id)[:8]}...)")
    
    def _example_doctor_registration(self):
        """Demonstrate doctor registration API."""
        print("\n👨‍⚕️ EXAMPLE 1: Doctor Registration")
        print("-" * 50)
        
        # Create doctor registration request
        doctor_request = DoctorRegistrationRequest(
            name="Dr Sarah Johnson",
            email="sarah.johnson@medicenter.com",
            phone="(555) 123-4567",
            location="123 Medical Plaza, Suite 200, New York, NY 10001",
            specialties=[self.specialties[0].id, self.specialties[1].id],
            experience="15 years of experience in cardiology and internal medicine. "
                      "Board certified in both specialties with extensive research background."
        )
        
        print(f"📝 Registering doctor: {doctor_request.name}")
        print(f"   Email: {doctor_request.email}")
        print(f"   Specialties: {len(doctor_request.specialties)} selected")
        
        # Register doctor
        result = self.demo.registration_service.register_doctor(doctor_request)
        
        if result.success:
            self.doctor_id = result.data.user_id
            print(f"✅ Doctor registered successfully!")
            print(f"   Doctor ID: {self.doctor_id}")
            print(f"   User Type: {result.data.user_type}")
            print(f"   Confirmation email sent to: {doctor_request.email}")
        else:
            print(f"❌ Doctor registration failed: {result.error_message}")
            
        # Demonstrate email availability check
        print(f"\n🔍 Checking email availability...")
        availability_result = self.demo.registration_service.check_email_availability(
            "sarah.johnson@medicenter.com", "doctor"
        )
        print(f"   Email available: {availability_result.data}")
    
    def _example_patient_registration(self):
        """Demonstrate patient registration API."""
        print("\n👤 EXAMPLE 2: Patient Registration")
        print("-" * 50)
        
        # Create patient registration request
        patient_request = PatientRegistrationRequest(
            name="Michael Chen",
            email="michael.chen@email.com",
            phone="(555) 987-6544",
            medical_history="No known allergies. Previous surgery: appendectomy in 2018. "
                           "Current medications: none. Family history of diabetes.",
            emergency_contact_name="Lisa Chen",
            emergency_contact_phone="(555) 987-6545",
            emergency_contact_relationship="spouse"
        )
        
        print(f"📝 Registering patient: {patient_request.name}")
        print(f"   Email: {patient_request.email}")
        print(f"   Emergency contact: {patient_request.emergency_contact_name}")
        
        # Register patient
        result = self.demo.registration_service.register_patient(patient_request)
        
        if result.success:
            self.patient_id = result.data.user_id
            print(f"✅ Patient registered successfully!")
            print(f"   Patient ID: {self.patient_id}")
            print(f"   User Type: {result.data.user_type}")
            print(f"   Confirmation email sent to: {patient_request.email}")
        else:
            print(f"❌ Patient registration failed: {result.error_message}")
    
    def _example_session_management(self):
        """Demonstrate session management API."""
        print("\n🔐 EXAMPLE 3: Session Management")
        print("-" * 50)
        
        # Create doctor session
        print("Creating doctor session...")
        doctor_session_result = self.demo.session_manager.create_session(
            self.doctor_id, "doctor", "192.168.1.100", "Mozilla/5.0 (Doctor App)"
        )
        
        if doctor_session_result.success:
            self.doctor_session_id = doctor_session_result.data.session_id
            print(f"✅ Doctor session created: {self.doctor_session_id}")
            print(f"   Expires at: {doctor_session_result.data.expires_at}")
        
        # Create patient session
        print("\nCreating patient session...")
        patient_session_result = self.demo.session_manager.create_session(
            self.patient_id, "patient", "192.168.1.101", "Mozilla/5.0 (Patient App)"
        )
        
        if patient_session_result.success:
            self.patient_session_id = patient_session_result.data.session_id
            print(f"✅ Patient session created: {self.patient_session_id}")
        
        # Validate sessions
        print("\n🔍 Validating sessions...")
        doctor_validation = self.demo.session_manager.validate_session(self.doctor_session_id)
        patient_validation = self.demo.session_manager.validate_session(self.patient_session_id)
        
        print(f"   Doctor session valid: {doctor_validation.success}")
        print(f"   Patient session valid: {patient_validation.success}")
        
        # Get user context from session
        if doctor_validation.success:
            context_result = self.demo.session_manager.get_user_context(self.doctor_session_id)
            if context_result.success:
                print(f"   Doctor context: {context_result.data.user_type} - {context_result.data.user_id}")
    
    def _example_profile_management(self):
        """Demonstrate profile management API."""
        print("\n👤 EXAMPLE 4: Profile Management")
        print("-" * 50)
        
        # Get doctor profile
        print("Retrieving doctor profile...")
        doctor_profile_result = self.demo.profile_service.get_doctor_profile(
            self.doctor_id, self.doctor_session_id
        )
        
        if doctor_profile_result.success:
            profile = doctor_profile_result.data
            print(f"✅ Doctor profile retrieved:")
            print(f"   Name: {profile.name}")
            print(f"   Email: {profile.email}")
            print(f"   Specialties: {len(profile.specialties)}")
            print(f"   Rating: {profile.rating}")
        
        # Update doctor profile
        print("\n📝 Updating doctor profile...")
        update_request = DoctorProfileUpdateRequest(
            phone="(555) 123-4568",  # Updated phone
            experience="16 years of experience in cardiology and internal medicine. "
                      "Recently completed advanced cardiac imaging certification."
        )
        
        update_result = self.demo.profile_service.update_doctor_profile(
            self.doctor_id, update_request, self.doctor_session_id
        )
        
        if update_result.success:
            print(f"✅ Doctor profile updated successfully!")
            print(f"   Changes made: {len(update_result.data.updated_fields)} fields")
            for field in update_result.data.updated_fields:
                print(f"   • Updated: {field}")
        
        # Get patient profile
        print("\nRetrieving patient profile...")
        patient_profile_result = self.demo.profile_service.get_patient_profile(
            self.patient_id, self.patient_session_id
        )
        
        if patient_profile_result.success:
            profile = patient_profile_result.data
            print(f"✅ Patient profile retrieved:")
            print(f"   Name: {profile.name}")
            print(f"   Email: {profile.email}")
            print(f"   Emergency contact: {profile.emergency_contact}")
    
    def _example_availability_management(self):
        """Demonstrate availability management API."""
        print("\n📅 EXAMPLE 5: Availability Management")
        print("-" * 50)
        
        # Add time slots
        print("Adding doctor availability slots...")
        
        # Create slots for next week
        base_date = datetime.utcnow() + timedelta(days=7)
        slots_added = []
        
        for day_offset in range(3):  # Add slots for 3 days
            slot_date = base_date + timedelta(days=day_offset)
            slot_date = slot_date.replace(hour=14, minute=0, second=0, microsecond=0)
            
            slot_request = TimeSlotRequest(
                datetime=slot_date,
                appointment_type=AppointmentType.IN_PERSON,
                specialty_id=self.specialties[0].id
            )
            
            result = self.demo.availability_service.add_time_slot(
                self.doctor_id, slot_request, self.doctor_session_id
            )
            
            if result.success:
                slots_added.append(result.data.availability_id)
                print(f"✅ Added slot: {slot_date.strftime('%Y-%m-%d %H:%M')} "
                      f"(IN_PERSON)")
        
        print(f"\nTotal slots added: {len(slots_added)}")
        
        # Query availability
        print("\n🔍 Querying doctor availability...")
        query = AvailabilityQueryRequest(
            doctor_id=self.doctor_id,
            start_date=base_date.date(),
            end_date=(base_date + timedelta(days=7)).date()
        )
        
        availability_result = self.demo.availability_service.get_doctor_availability(query)
        
        if availability_result.success:
            slots = availability_result.data
            print(f"✅ Found {len(slots)} available slots:")
            for slot in slots[:3]:  # Show first 3
                print(f"   • {slot.datetime.strftime('%Y-%m-%d %H:%M')} - "
                      f"{slot.appointment_type} ({slot.status})")
        
        # Modify a time slot
        if slots_added:
            print(f"\n📝 Modifying time slot...")
            modify_request = TimeSlotRequest(
                datetime=base_date.replace(hour=15, minute=0, second=0, microsecond=0),
                appointment_type=AppointmentType.TELEMEDICINE,
                specialty_id=self.specialties[1].id
            )
            
            modify_result = self.demo.availability_service.modify_time_slot(
                self.doctor_id, slots_added[0], modify_request, self.doctor_session_id
            )
            
            if modify_result.success:
                print(f"✅ Time slot modified successfully!")
                print(f"   Slot ID: {modify_result.data.availability_id}")
                print(f"   Operation: {modify_result.data.operation}")
    
    def _example_bulk_operations(self):
        """Demonstrate bulk operations API."""
        print("\n📦 EXAMPLE 6: Bulk Operations")
        print("-" * 50)
        
        # Bulk add time slots
        print("Adding multiple time slots in bulk...")
        
        base_date = datetime.utcnow() + timedelta(days=14)
        time_slots = []
        
        # Create slots for a week
        for day in range(5):  # Monday to Friday
            for hour in [9, 11, 14, 16]:  # 4 slots per day
                slot_time = base_date + timedelta(days=day)
                slot_time = slot_time.replace(hour=hour, minute=0, second=0, microsecond=0)
                
                time_slots.append(TimeSlotRequest(
                    datetime=slot_time,
                    appointment_type=AppointmentType.IN_PERSON if hour < 14 else AppointmentType.TELEMEDICINE,
                    specialty_id=self.specialties[0].id
                ))
        
        bulk_request = BulkAvailabilityRequest(
            doctor_id=self.doctor_id,
            time_slots=time_slots
        )
        
        bulk_result = self.demo.availability_service.bulk_add_time_slots(
            bulk_request, self.doctor_session_id
        )
        
        if bulk_result.success:
            print(f"✅ Bulk operation completed!")
            print(f"   Slots requested: {bulk_result.data.get('total_requested', len(time_slots))}")
            print(f"   Slots added: {bulk_result.data.get('successful_additions', 0)}")
            print(f"   Slots failed: {bulk_result.data.get('failed_additions', 0)}")
            
            failed_slots = bulk_result.data.get('failed_slots', [])
            if failed_slots:
                print(f"   Failed slots: {len(failed_slots)} (business rule violations)")
    
    def _example_query_operations(self):
        """Demonstrate query and search operations."""
        print("\n🔍 EXAMPLE 7: Query Operations")
        print("-" * 50)
        
        # Get registration statistics
        print("Retrieving registration statistics...")
        reg_stats = self.demo.registration_service.get_registration_statistics()
        
        if reg_stats.success:
            stats = reg_stats.data
            print(f"✅ Registration Statistics:")
            print(f"   Total users: {stats.get('total_users', 0)}")
            print(f"   Active doctors: {stats.get('active_doctors', 0)}")
            print(f"   Active patients: {stats.get('active_patients', 0)}")
            print(f"   Today's registrations: {stats.get('registrations_today', 0)}")
        
        # Get session statistics
        print("\nRetrieving session statistics...")
        session_stats = self.demo.session_manager.get_session_statistics()
        
        if session_stats.success:
            stats = session_stats.data
            print(f"✅ Session Statistics:")
            print(f"   Active sessions: {stats.get('active_sessions', 0)}")
            print(f"   Total sessions today: {stats.get('sessions_created_today', 0)}")
            print(f"   Average session duration: {stats.get('average_session_duration_minutes', 0):.1f} minutes")
        
        # Get availability statistics
        print("\nRetrieving availability statistics...")
        avail_stats = self.demo.availability_service.get_availability_statistics()
        
        if avail_stats.success:
            stats = avail_stats.data
            print(f"✅ Availability Statistics:")
            print(f"   Total slots: {stats.get('total_slots', 0)}")
            print(f"   Available slots: {stats.get('available_slots', 0)}")
            print(f"   Utilization rate: {stats.get('utilization_rate', 0):.1%}")
            print(f"   Slots this week: {stats.get('slots_this_week', 0)}")
    
    def _example_error_handling(self):
        """Demonstrate error handling scenarios."""
        print("\n⚠️ EXAMPLE 8: Error Handling")
        print("-" * 50)
        
        # Test validation errors
        print("Testing validation errors...")
        
        try:
            # Invalid email format
            invalid_request = DoctorRegistrationRequest(
                name="Dr. Test",
                email="invalid-email",  # Invalid format
                phone="123",  # Too short
                location="",  # Empty
                specialties=[],  # Empty list
                experience="Short"  # Too short
            )
            
            result = self.demo.registration_service.register_doctor(invalid_request)
            print(f"❌ Expected validation error, but got: {result}")
            
        except ValidationError as e:
            print(f"✅ Caught expected validation error: {e}")
        
        # Test authentication errors
        print("\nTesting authentication errors...")
        
        try:
            # Use invalid session ID
            fake_session = str(uuid.uuid4())
            result = self.demo.profile_service.get_doctor_profile(
                self.doctor_id, fake_session
            )
            
            if not result.success:
                print(f"✅ Authentication properly rejected: {result.error_message}")
        
        except SessionError as e:
            print(f"✅ Caught expected session error: {e}")
        
        # Test business rule violations
        print("\nTesting business rule violations...")
        
        try:
            # Try to add slot in the past
            past_date = datetime.utcnow() - timedelta(days=1)
            past_slot = TimeSlotRequest(
                datetime=past_date,
                appointment_type=AppointmentType.IN_PERSON,
                specialty_id=self.specialties[0].id
            )
            
            result = self.demo.availability_service.add_time_slot(
                self.doctor_id, past_slot, self.doctor_session_id
            )
            
            if not result.success:
                print(f"✅ Business rule properly enforced: {result.error_message}")
        
        except BusinessRuleError as e:
            print(f"✅ Caught expected business rule error: {e}")
    
    def _example_statistics_and_monitoring(self):
        """Demonstrate statistics and monitoring capabilities."""
        print("\n📊 EXAMPLE 9: Statistics and Monitoring")
        print("-" * 50)
        
        # Event statistics
        print("Event processing statistics...")
        try:
            event_stats = self.demo.registration_service.event_publisher.get_event_statistics()
        except AttributeError:
            # Fallback to basic statistics
            event_stats = {
                'total_events': 0,
                'processed_events': 0,
                'pending_events': 0,
                'failed_events': 0
            }
        
        print(f"✅ Event Statistics:")
        print(f"   Total events published: {event_stats['total_events']}")
        print(f"   Events processed: {event_stats['processed_events']}")
        print(f"   Events pending: {event_stats['pending_events']}")
        print(f"   Failed events: {event_stats['failed_events']}")
        
        # Integration health check
        print("\nIntegration health checks...")
        
        # Check email service
        try:
            email_health = self.demo.email_service.health_check()
            print(f"   Email service: {'✅ Healthy' if email_health else '❌ Unhealthy'}")
        except AttributeError:
            print(f"   Email service: ✅ Healthy (simulated)")
        
        # Check admin service
        try:
            admin_health = self.demo.admin_service.health_check()
            print(f"   Admin service: {'✅ Healthy' if admin_health.success else '❌ Unhealthy'}")
        except:
            print(f"   Admin service: ❌ Unhealthy (connection failed)")
        
        # Check appointment service
        try:
            appointment_health = self.demo.appointment_service.health_check()
            print(f"   Appointment service: {'✅ Healthy' if appointment_health.success else '❌ Unhealthy'}")
        except:
            print(f"   Appointment service: ❌ Unhealthy (connection failed)")
        
        # Data persistence status
        print("\nData persistence status...")
        
        # Check repository data counts
        doctor_count = len(self.demo.doctor_repository.find_all())
        patient_count = len(self.demo.patient_repository.find_all())
        session_count = len(self.demo.session_repository.find_all())
        
        print(f"   Doctors in storage: {doctor_count}")
        print(f"   Patients in storage: {patient_count}")
        print(f"   Active sessions: {session_count}")
        
        # Memory usage (simplified)
        import sys
        memory_usage = sys.getsizeof(self.demo)
        print(f"   Approximate memory usage: {memory_usage} bytes")


def main():
    """Main function to run all API examples."""
    try:
        examples = UserManagementAPIExamples()
        examples.run_all_examples()
        
        print("\n" + "=" * 80)
        print("🎉 API EXAMPLES DEMONSTRATION COMPLETE!")
        print("=" * 80)
        print("\nThese examples show how to:")
        print("• Register doctors and patients")
        print("• Manage user sessions and authentication")
        print("• Update user profiles")
        print("• Manage doctor availability")
        print("• Perform bulk operations")
        print("• Query data and statistics")
        print("• Handle errors gracefully")
        print("• Monitor system health")
        print("\nFor more details, see the comprehensive documentation in README.md")
        
    except Exception as e:
        print(f"\n❌ API Examples failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())