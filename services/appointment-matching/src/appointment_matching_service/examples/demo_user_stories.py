#!/usr/bin/env python3
"""
Demo script showing all user story implementations for the Appointment Matching Service.
"""

import sys
import os
from datetime import datetime, timedelta
from decimal import Decimal

# Add the parent directory to the path so we can import the service
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from appointment_matching_service.services.appointment_matching_service import AppointmentMatchingService
from appointment_matching_service.models.doctor import Doctor
from appointment_matching_service.models.patient import Patient
from appointment_matching_service.models.medical_specialty import MedicalSpecialty
from appointment_matching_service.utils.enums import UserStatus, AppointmentType


def setup_sample_data(service):
    """Set up sample doctors, patients, and specialties."""
    print("Setting up sample data...")
    
    # Create medical specialties
    cardiology = MedicalSpecialty(
        name="Cardiology",
        description="Heart and cardiovascular system"
    )
    
    neurology = MedicalSpecialty(
        name="Neurology", 
        description="Brain and nervous system"
    )
    
    # Create sample doctors
    doctor1 = Doctor(
        name="Dr. Sarah Johnson",
        email="sarah.johnson@hospital.com",
        phone="+1-555-0101",
        location="New York, NY",
        specialties=[cardiology.id],
        experience="15 years of cardiology experience, specialized in interventional cardiology",
        rating=Decimal('4.8')
    )
    
    doctor2 = Doctor(
        name="Dr. Michael Chen",
        email="michael.chen@hospital.com", 
        phone="+1-555-0102",
        location="New York, NY",
        specialties=[neurology.id],
        experience="12 years of neurology experience, specialized in headache disorders",
        rating=Decimal('4.6')
    )
    
    doctor3 = Doctor(
        name="Dr. Emily Rodriguez",
        email="emily.rodriguez@hospital.com",
        phone="+1-555-0103", 
        location="New York, NY",
        specialties=[cardiology.id, neurology.id],
        experience="10 years of general medicine with cardiology and neurology focus",
        rating=Decimal('4.4')
    )
    
    # Create sample patients
    patient1 = Patient(
        name="John Smith",
        email="john.smith@email.com",
        phone="+1-555-0201",
        medical_history="History of hypertension, no known allergies",
        emergency_contact_name="Mary Smith",
        emergency_contact_phone="+1-555-0202",
        emergency_contact_relationship="Wife"
    )
    
    patient2 = Patient(
        name="Lisa Wilson", 
        email="lisa.wilson@email.com",
        phone="+1-555-0203",
        medical_history="Occasional migraines, no current medications",
        emergency_contact_name="Robert Wilson",
        emergency_contact_phone="+1-555-0204", 
        emergency_contact_relationship="Husband"
    )
    
    # Save to repositories
    saved_doctors = [
        service.doctor_repository.create(doctor1),
        service.doctor_repository.create(doctor2), 
        service.doctor_repository.create(doctor3)
    ]
    
    saved_patients = [
        service.patient_repository.create(patient1),
        service.patient_repository.create(patient2)
    ]
    
    print(f"Created {len(saved_doctors)} doctors and {len(saved_patients)} patients")
    return saved_doctors, saved_patients


def demo_us_p003_describe_symptoms(service, patient):
    """Demo US-P003: Describe Symptoms"""
    print("\n" + "="*60)
    print("US-P003: DESCRIBE SYMPTOMS")
    print("="*60)
    
    symptoms_text = "I have been experiencing severe chest pain and shortness of breath for the past two days. The pain gets worse when I exercise and I feel dizzy sometimes."
    
    print(f"Patient: {patient.name}")
    print(f"Symptoms: {symptoms_text}")
    
    # Process symptom description
    symptom_desc = service.describe_symptoms(
        patient_id=patient.id,
        symptoms_text=symptoms_text
    )
    
    print(f"\nAnalysis Results:")
    print(f"- Symptom ID: {symptom_desc.id}")
    print(f"- Keywords extracted: {symptom_desc.parsed_keywords}")
    print(f"- Confidence score: {symptom_desc.confidence_score}")
    print(f"- Matched specialties: {len(symptom_desc.matched_specialties)}")
    print(f"- Analysis timestamp: {symptom_desc.analysis_timestamp}")
    
    return symptom_desc


def demo_us_p004_doctor_recommendations(service, symptom_desc):
    """Demo US-P004: View Doctor Recommendations"""
    print("\n" + "="*60)
    print("US-P004: VIEW DOCTOR RECOMMENDATIONS")
    print("="*60)
    
    print(f"Getting recommendations for symptom description: {symptom_desc.id}")
    
    # Get doctor recommendations
    recommendations = service.get_doctor_recommendations(symptom_desc.id)
    
    print(f"\nRecommendation Results:")
    print(f"- Recommendation ID: {recommendations.id}")
    print(f"- Number of doctors: {recommendations.get_recommendation_count()}")
    print(f"- Algorithm version: {recommendations.algorithm_version}")
    
    # Show ranked recommendations
    ranked_recs = recommendations.get_recommendations_sorted()
    for i, (doctor_id, score, slot) in enumerate(ranked_recs, 1):
        doctor = service.doctor_repository.find_by_id(doctor_id)
        print(f"\n{i}. Dr. {doctor.name if doctor else 'Unknown'}")
        print(f"   - Match Score: {score}")
        print(f"   - Rating: {doctor.rating if doctor else 'N/A'}")
        print(f"   - Available Slot: {slot}")
        print(f"   - Experience: {doctor.experience[:50] + '...' if doctor and len(doctor.experience) > 50 else doctor.experience if doctor else 'N/A'}")
    
    return recommendations


def demo_us_p006_book_appointment(service, patient, recommendations):
    """Demo US-P006: Book Appointment"""
    print("\n" + "="*60)
    print("US-P006: BOOK APPOINTMENT")
    print("="*60)
    
    # Get the top recommended doctor
    top_recommendation = recommendations.get_top_recommendation()
    if not top_recommendation:
        print("No recommendations available for booking")
        return None
    
    doctor_id, match_score, available_slot = top_recommendation
    doctor = service.doctor_repository.find_by_id(doctor_id)
    
    print(f"Booking appointment with: Dr. {doctor.name}")
    print(f"Patient: {patient.name}")
    print(f"Proposed time: {available_slot}")
    
    # Book the appointment
    appointment = service.book_appointment(
        patient_id=patient.id,
        doctor_id=doctor_id,
        appointment_datetime=available_slot,
        symptoms="Severe chest pain and shortness of breath, gets worse with exercise, occasional dizziness"
    )
    
    print(f"\nAppointment Booked Successfully!")
    print(f"- Appointment ID: {appointment.id}")
    print(f"- Status: {appointment.status.value}")
    print(f"- Date/Time: {appointment.datetime}")
    print(f"- Type: {appointment.appointment_type.value}")
    print(f"- Reschedule count: {appointment.reschedule_count}")
    
    return appointment


def demo_us_p007_view_appointments(service, patient):
    """Demo US-P007: View My Appointments"""
    print("\n" + "="*60)
    print("US-P007: VIEW MY APPOINTMENTS")
    print("="*60)
    
    print(f"Getting appointments for patient: {patient.name}")
    
    # Get patient appointments
    appointments = service.get_patient_appointments(patient.id)
    
    print(f"\nFound {len(appointments)} appointments:")
    
    for i, appointment in enumerate(appointments, 1):
        doctor = service.doctor_repository.find_by_id(appointment.doctor_id)
        print(f"\n{i}. Appointment {appointment.id}")
        print(f"   - Doctor: Dr. {doctor.name if doctor else 'Unknown'}")
        print(f"   - Date/Time: {appointment.datetime}")
        print(f"   - Status: {appointment.status.value}")
        print(f"   - Type: {appointment.appointment_type.value}")
        print(f"   - Symptoms: {appointment.symptoms[:50] + '...' if len(appointment.symptoms) > 50 else appointment.symptoms}")
        if appointment.reschedule_reason:
            print(f"   - Reschedule reason: {appointment.reschedule_reason}")
    
    return appointments


def demo_us_p008_reschedule_appointment(service, appointment):
    """Demo US-P008: Reschedule Appointment"""
    print("\n" + "="*60)
    print("US-P008: RESCHEDULE APPOINTMENT")
    print("="*60)
    
    print(f"Rescheduling appointment: {appointment.id}")
    print(f"Current time: {appointment.datetime}")
    print(f"Current reschedule count: {appointment.reschedule_count}")
    
    # Calculate new time (2 days later)
    new_datetime = appointment.datetime + timedelta(days=2)
    reschedule_reason = "Patient has a work conflict and needs to reschedule"
    
    print(f"New proposed time: {new_datetime}")
    print(f"Reason: {reschedule_reason}")
    
    # Reschedule the appointment
    rescheduled_appointment = service.reschedule_appointment(
        appointment_id=appointment.id,
        new_datetime=new_datetime,
        reason=reschedule_reason
    )
    
    print(f"\nAppointment Rescheduled Successfully!")
    print(f"- New Date/Time: {rescheduled_appointment.datetime}")
    print(f"- Status: {rescheduled_appointment.status.value}")
    print(f"- Reschedule count: {rescheduled_appointment.reschedule_count}")
    print(f"- Reschedule reason: {rescheduled_appointment.reschedule_reason}")
    
    return rescheduled_appointment


def demo_us_d005_doctor_view_appointments(service, doctors):
    """Demo US-D005: Doctor View Appointments"""
    print("\n" + "="*60)
    print("US-D005: DOCTOR VIEW APPOINTMENTS")
    print("="*60)
    
    # Show appointments for the first doctor
    doctor = doctors[0]
    print(f"Getting appointments for doctor: Dr. {doctor.name}")
    
    # Get doctor appointments
    appointments = service.get_doctor_appointments(doctor.id)
    
    print(f"\nFound {len(appointments)} appointments:")
    
    for i, appointment in enumerate(appointments, 1):
        patient = service.patient_repository.find_by_id(appointment.patient_id)
        print(f"\n{i}. Appointment {appointment.id}")
        print(f"   - Patient: {patient.name if patient else 'Unknown'}")
        print(f"   - Date/Time: {appointment.datetime}")
        print(f"   - Status: {appointment.status.value}")
        print(f"   - Type: {appointment.appointment_type.value}")
        print(f"   - Symptoms: {appointment.symptoms}")
        if patient:
            print(f"   - Emergency Contact: {patient.emergency_contact_name} ({patient.emergency_contact_relationship})")
            print(f"   - Emergency Phone: {patient.emergency_contact_phone}")
    
    return appointments


def demo_service_stats(service):
    """Demo service statistics"""
    print("\n" + "="*60)
    print("SERVICE STATISTICS")
    print("="*60)
    
    stats = service.get_service_stats()
    
    print("Current service statistics:")
    for key, value in stats.items():
        print(f"- {key.replace('_', ' ').title()}: {value}")


def main():
    """Main demo function"""
    print("APPOINTMENT MATCHING SERVICE - USER STORY DEMONSTRATIONS")
    print("=" * 80)
    
    # Initialize the service
    service = AppointmentMatchingService()
    
    # Set up sample data
    doctors, patients = setup_sample_data(service)
    
    # Use the first patient for demos
    patient = patients[0]
    
    # Demo all user stories in sequence
    symptom_desc = demo_us_p003_describe_symptoms(service, patient)
    recommendations = demo_us_p004_doctor_recommendations(service, symptom_desc)
    appointment = demo_us_p006_book_appointment(service, patient, recommendations)
    
    if appointment:
        demo_us_p007_view_appointments(service, patient)
        rescheduled_appointment = demo_us_p008_reschedule_appointment(service, appointment)
    
    demo_us_d005_doctor_view_appointments(service, doctors)
    demo_service_stats(service)
    
    print("\n" + "="*80)
    print("DEMO COMPLETED SUCCESSFULLY!")
    print("All user stories have been demonstrated.")
    print("="*80)


if __name__ == "__main__":
    main()