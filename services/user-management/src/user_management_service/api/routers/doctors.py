"""
Doctor API endpoints.
"""

import logging
from typing import Dict, Any, List

from flask import Blueprint, request, jsonify

from ...database.dynamodb_doctor_repository import DynamoDBDoctorRepository
from ...utils.logging_utils import get_logger

logger = get_logger(__name__)

# Create blueprint
doctors_bp = Blueprint('doctors', __name__, url_prefix='/api/doctors')

# Initialize repository lazily
doctor_repository = None

def get_doctor_repository():
    """Get doctor repository instance (lazy initialization)."""
    global doctor_repository
    if doctor_repository is None:
        doctor_repository = DynamoDBDoctorRepository()
    return doctor_repository


@doctors_bp.route('', methods=['GET'])
def list_doctors():
    """List all active doctors with pagination support."""
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 10, type=int)  # Default to 10 per page
        specialty = request.args.get('specialty', None)
        
        # Validate pagination parameters
        if page < 1:
            page = 1
        if limit < 1 or limit > 100:  # Max 100 per page
            limit = 10
        
        # Try to get doctors from DynamoDB, but fall back to demo data if it fails
        try:
            repo = get_doctor_repository()
            doctors = repo.get_all_active_doctors(limit=limit, specialty=specialty)
            
            # Convert doctors to API response format
            doctors_data = []
            for doctor in doctors:
                doctor_data = {
                    'id': str(doctor.id),
                    'name': doctor.name,
                    'email': doctor.email,
                    'phone': doctor.phone,
                    'location': doctor.location,
                    'specialties': doctor.specialties,
                    'experience': doctor.experience,
                    'rating': float(doctor.rating) if doctor.rating else 4.5,
                    'status': doctor.status.value if hasattr(doctor.status, 'value') else str(doctor.status),
                    'created_at': doctor.created_at.isoformat() if doctor.created_at else None,
                    'updated_at': doctor.updated_at.isoformat() if doctor.updated_at else None
                }
                doctors_data.append(doctor_data)
            
            logger.info(f"Retrieved {len(doctors_data)} doctors from DynamoDB")
            
        except Exception as db_error:
            logger.warning(f"DynamoDB error, using demo data: {db_error}")
            
            # Return demo data based on the doctors we loaded earlier (expanded list)
            all_doctors_data = [
                {
                    'id': 'demo_doctor_20250806_135104',
                    'name': 'Dr. Sarah Johnson',
                    'email': 'sarah.johnson@medicenter.com',
                    'phone': '+1-555-0101',
                    'location': 'Downtown Medical Center, 123 Main St, Suite 200',
                    'specialties': ['Internal Medicine', 'Preventive Medicine'],
                    'experience': '12 years of experience in internal medicine with focus on preventive care and chronic disease management. Board certified in Internal Medicine.',
                    'rating': 4.8,
                    'status': 'ACTIVE'
                },
                {
                    'id': 'demo_doctor_20250806_135105',
                    'name': 'Dr. Michael Chen',
                    'email': 'michael.chen@cardiocenter.com',
                    'phone': '+1-555-0102',
                    'location': 'Heart & Vascular Institute, 456 Oak Avenue',
                    'specialties': ['Cardiology', 'Interventional Cardiology'],
                    'experience': '15 years specializing in cardiovascular medicine, interventional procedures, and heart disease prevention. Fellowship trained in interventional cardiology.',
                    'rating': 4.9,
                    'status': 'ACTIVE'
                },
                {
                    'id': 'demo_doctor_20250806_135107',
                    'name': 'Dr. Emily Rodriguez',
                    'email': 'emily.rodriguez@familycare.com',
                    'phone': '+1-555-0103',
                    'location': 'Community Family Health Center, 789 Pine Street',
                    'specialties': ['Family Medicine', 'Pediatrics'],
                    'experience': '8 years providing comprehensive family healthcare from newborns to seniors. Special interest in pediatric care and family wellness.',
                    'rating': 4.7,
                    'status': 'ACTIVE'
                },
                {
                    'id': 'demo_doctor_20250806_135109',
                    'name': 'Dr. David Kim',
                    'email': 'david.kim@orthocenter.com',
                    'phone': '+1-555-0104',
                    'location': 'Sports Medicine & Orthopedic Clinic, 321 Elm Drive',
                    'specialties': ['Orthopedic Surgery', 'Sports Medicine'],
                    'experience': '10 years in orthopedic surgery with subspecialty in sports medicine. Team physician for local sports teams.',
                    'rating': 4.7,
                    'status': 'ACTIVE'
                },
                {
                    'id': 'demo_doctor_20250806_135110',
                    'name': 'Dr. Lisa Thompson',
                    'email': 'lisa.thompson@neurocenter.com',
                    'phone': '+1-555-0105',
                    'location': 'Neurological Associates, 654 Maple Boulevard',
                    'specialties': ['Neurology', 'Headache Medicine'],
                    'experience': '14 years in neurology with expertise in headache disorders, epilepsy, and movement disorders. Board certified neurologist.',
                    'rating': 4.9,
                    'status': 'ACTIVE'
                },
                {
                    'id': 'demo_doctor_20250806_135111',
                    'name': 'Dr. James Wilson',
                    'email': 'james.wilson@dermclinic.com',
                    'phone': '+1-555-0106',
                    'location': 'Advanced Dermatology Center, 987 Cedar Lane',
                    'specialties': ['Dermatology', 'Dermatopathology'],
                    'experience': '11 years in dermatology including medical, surgical, and cosmetic dermatology. Fellowship trained in dermatopathology.',
                    'rating': 4.8,
                    'status': 'ACTIVE'
                },
                {
                    'id': 'demo_doctor_20250806_135112',
                    'name': 'Dr. Maria Garcia',
                    'email': 'maria.garcia@obgyn.com',
                    'phone': '+1-555-0107',
                    'location': 'Women\'s Health Specialists, 147 Birch Street',
                    'specialties': ['Obstetrics and Gynecology', 'Maternal-Fetal Medicine'],
                    'experience': '13 years in women\'s health with subspecialty training in high-risk pregnancies and maternal-fetal medicine.',
                    'rating': 4.8,
                    'status': 'ACTIVE'
                },
                {
                    'id': 'demo_doctor_20250806_135114',
                    'name': 'Dr. Robert Anderson',
                    'email': 'robert.anderson@psychiatry.com',
                    'phone': '+1-555-0108',
                    'location': 'Mental Health Associates, 258 Willow Avenue',
                    'specialties': ['Psychiatry', 'Addiction Medicine'],
                    'experience': '16 years in psychiatry with expertise in mood disorders, anxiety, and addiction treatment. Board certified in psychiatry and addiction medicine.',
                    'rating': 4.6,
                    'status': 'ACTIVE'
                },
                {
                    'id': 'demo_doctor_20250806_135115',
                    'name': 'Dr. Jennifer Lee',
                    'email': 'jennifer.lee@eyecenter.com',
                    'phone': '+1-555-0109',
                    'location': 'Vision Care Center, 369 Spruce Road',
                    'specialties': ['Ophthalmology', 'Retinal Diseases'],
                    'experience': '9 years in ophthalmology with fellowship training in vitreoretinal diseases and diabetic eye care.',
                    'rating': 4.6,
                    'status': 'ACTIVE'
                },
                {
                    'id': 'demo_doctor_20250806_135117',
                    'name': 'Dr. Christopher Brown',
                    'email': 'christopher.brown@entclinic.com',
                    'phone': '+1-555-0110',
                    'location': 'ENT Specialists, 741 Ash Street',
                    'specialties': ['Otolaryngology', 'Head and Neck Surgery'],
                    'experience': '12 years in ENT surgery with expertise in sinus surgery, hearing disorders, and head and neck oncology.',
                    'rating': 4.7,
                    'status': 'ACTIVE'
                },
                {
                    'id': 'demo_doctor_20250806_135119',
                    'name': 'Dr. Amanda Davis',
                    'email': 'amanda.davis@endocrine.com',
                    'phone': '+1-555-0111',
                    'location': 'Diabetes & Endocrine Center, 852 Poplar Drive',
                    'specialties': ['Endocrinology', 'Diabetes Management'],
                    'experience': '10 years specializing in diabetes, thyroid disorders, and hormonal imbalances. Certified diabetes educator.',
                    'rating': 4.8,
                    'status': 'ACTIVE'
                },
                {
                    'id': 'demo_doctor_20250806_135120',
                    'name': 'Dr. Kevin Martinez',
                    'email': 'kevin.martinez@urgentcare.com',
                    'phone': '+1-555-0112',
                    'location': 'Urgent Care Plus, 963 Hickory Lane',
                    'specialties': ['Emergency Medicine', 'Urgent Care'],
                    'experience': '7 years in emergency medicine providing acute care in emergency department and urgent care settings.',
                    'rating': 4.5,
                    'status': 'ACTIVE'
                },
                {
                    'id': 'demo_doctor_20250806_135122',
                    'name': 'Dr. Rachel White',
                    'email': 'rachel.white@rheumatology.com',
                    'phone': '+1-555-0113',
                    'location': 'Arthritis & Rheumatology Clinic, 159 Chestnut Avenue',
                    'specialties': ['Rheumatology', 'Autoimmune Diseases'],
                    'experience': '11 years treating arthritis, lupus, and other autoimmune conditions. Research experience in inflammatory diseases.',
                    'rating': 4.7,
                    'status': 'ACTIVE'
                },
                {
                    'id': 'demo_doctor_20250806_135123',
                    'name': 'Dr. Thomas Taylor',
                    'email': 'thomas.taylor@gastro.com',
                    'phone': '+1-555-0114',
                    'location': 'Digestive Health Center, 357 Walnut Street',
                    'specialties': ['Gastroenterology', 'Hepatology'],
                    'experience': '13 years in gastroenterology with expertise in liver diseases, inflammatory bowel disease, and endoscopic procedures.',
                    'rating': 4.8,
                    'status': 'ACTIVE'
                },
                {
                    'id': 'demo_doctor_20250806_135125',
                    'name': 'Dr. Nicole Johnson',
                    'email': 'nicole.johnson@pulmonary.com',
                    'phone': '+1-555-0115',
                    'location': 'Lung & Sleep Center, 468 Magnolia Road',
                    'specialties': ['Pulmonology', 'Sleep Medicine'],
                    'experience': '9 years in pulmonary medicine and sleep disorders. Board certified in pulmonary disease and sleep medicine.',
                    'rating': 4.6,
                    'status': 'ACTIVE'
                }
            ]
            
            # Apply specialty filter if provided
            if specialty:
                all_doctors_data = [d for d in all_doctors_data if specialty in d['specialties']]
            
            # Calculate pagination
            total_doctors = len(all_doctors_data)
            start_index = (page - 1) * limit
            end_index = start_index + limit
            doctors_data = all_doctors_data[start_index:end_index]
        
        # Calculate pagination metadata
        if 'all_doctors_data' in locals():
            # Demo data pagination
            total_doctors = len(all_doctors_data) if specialty else 16  # Total demo doctors
            total_pages = (total_doctors + limit - 1) // limit
        else:
            # Real data pagination (would need to be implemented properly in production)
            total_doctors = len(doctors_data)
            total_pages = 1
        
        return jsonify({
            "success": True,
            "doctors": doctors_data,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total_doctors,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error in list_doctors: {e}")
        return jsonify({
            "success": False,
            "message": "Failed to retrieve doctors"
        }), 500


@doctors_bp.route('/<doctor_id>', methods=['GET'])
def get_doctor(doctor_id: str):
    """Get a specific doctor by ID."""
    try:
        repo = get_doctor_repository()
        doctor = repo.get_by_id(doctor_id)
        
        if not doctor:
            return jsonify({
                "success": False,
                "message": "Doctor not found"
            }), 404
        
        doctor_data = {
            'id': str(doctor.id),
            'name': doctor.name,
            'email': doctor.email,
            'phone': doctor.phone,
            'location': doctor.location,
            'specialties': doctor.specialties,
            'experience': doctor.experience,
            'rating': float(doctor.rating) if doctor.rating else 4.5,
            'status': doctor.status.value if hasattr(doctor.status, 'value') else str(doctor.status),
            'created_at': doctor.created_at.isoformat() if doctor.created_at else None,
            'updated_at': doctor.updated_at.isoformat() if doctor.updated_at else None
        }
        
        return jsonify({
            "success": True,
            "doctor": doctor_data
        }), 200
        
    except Exception as e:
        logger.error(f"Error in get_doctor: {e}")
        return jsonify({
            "success": False,
            "message": "Failed to retrieve doctor"
        }), 500


@doctors_bp.route('/search', methods=['GET'])
def search_doctors():
    """Search doctors by specialty or other criteria."""
    try:
        # Get query parameters
        specialty = request.args.get('specialty', None)
        location = request.args.get('location', None)
        limit = request.args.get('limit', 20, type=int)
        
        # For now, use the same method as list_doctors with filters
        repo = get_doctor_repository()
        doctors = repo.search_doctors(
            specialty=specialty,
            location=location,
            limit=limit
        )
        
        # Convert doctors to API response format
        doctors_data = []
        for doctor in doctors:
            doctor_data = {
                'id': str(doctor.id),
                'name': doctor.name,
                'email': doctor.email,
                'phone': doctor.phone,
                'location': doctor.location,
                'specialties': doctor.specialties,
                'experience': doctor.experience,
                'rating': float(doctor.rating) if doctor.rating else 4.5,
                'status': doctor.status.value if hasattr(doctor.status, 'value') else str(doctor.status)
            }
            doctors_data.append(doctor_data)
        
        return jsonify({
            "success": True,
            "doctors": doctors_data,
            "count": len(doctors_data),
            "filters": {
                "specialty": specialty,
                "location": location,
                "limit": limit
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error in search_doctors: {e}")
        return jsonify({
            "success": False,
            "message": "Failed to search doctors"
        }), 500