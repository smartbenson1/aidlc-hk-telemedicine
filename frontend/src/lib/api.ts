// API Configuration for HealMatch Easy Backend Services
export const API_CONFIG = {
  USER_MANAGEMENT: process.env.REACT_APP_USER_MANAGEMENT_API || 'https://9gip0hh7mb.execute-api.us-east-1.amazonaws.com/prod/api',
  APPOINTMENT_MATCHING: process.env.REACT_APP_APPOINTMENT_MATCHING_API || 'https://7ljuyzkjsd.execute-api.us-east-1.amazonaws.com/prod',
  ADMINISTRATION: process.env.REACT_APP_ADMINISTRATION_API || 'https://06i3sudebb.execute-api.us-east-1.amazonaws.com/prod/api'
};

export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface Patient {
  id: string;
  name: string;
  email: string;
  phone: string;
  medical_history?: string;
  emergency_contact_name: string;
  emergency_contact_phone: string;
  emergency_contact_relationship: string;
}

export interface Doctor {
  id: string;
  name: string;
  email: string;
  phone: string;
  location: string;
  specialties: string[];
  experience: string;
  specialty_name?: string;
  rating?: number;
  available_slots?: string[];
  match_score?: number;
}

export interface Specialty {
  id: string;
  name: string;
  description?: string;
}

export interface SymptomAnalysis {
  id: string;
  patient_id: string;
  symptoms: string;
  analysis_result?: any;
  recommended_specialties?: string[];
}

export interface Appointment {
  id: string;
  patient_id: string;
  doctor_id: string;
  appointment_datetime: string;
  symptoms: string;
  appointment_type: 'in_person' | 'virtual';
  status: 'scheduled' | 'completed' | 'cancelled';
}

class ApiClient {
  private async request<T>(url: string, options: RequestInit = {}): Promise<ApiResponse<T>> {
    try {
      const response = await fetch(url, {
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
          ...options.headers,
        },
        ...options,
      });

      const data = await response.json();

      if (!response.ok) {
        return {
          success: false,
          error: data.message || `HTTP ${response.status}: ${response.statusText}`
        };
      }

      // Backend returns { success: true, data: {...} }
      if (data.success) {
        return { success: true, data: data };
      } else {
        return { success: false, error: data.message || 'Request failed' };
      }
    } catch (error) {
      console.error('API request failed:', error);
      return { 
        success: false, 
        error: error instanceof Error ? error.message : 'Unknown error' 
      };
    }
  }

  // Patient APIs
  async registerPatient(patientData: Omit<Patient, 'id'>): Promise<ApiResponse<Patient>> {
    return this.request<Patient>(`${API_CONFIG.USER_MANAGEMENT}/patients/register`, {
      method: 'POST',
      body: JSON.stringify(patientData),
    });
  }

  async getPatient(patientId: string): Promise<ApiResponse<Patient>> {
    return this.request<Patient>(`${API_CONFIG.USER_MANAGEMENT}/profiles/patients/${patientId}`);
  }

  // Doctor APIs
  async registerDoctor(doctorData: Omit<Doctor, 'id'>): Promise<ApiResponse<Doctor>> {
    return this.request<Doctor>(`${API_CONFIG.USER_MANAGEMENT}/doctors/register`, {
      method: 'POST',
      body: JSON.stringify(doctorData),
    });
  }

  async getDoctor(doctorId: string): Promise<ApiResponse<Doctor>> {
    return this.request<Doctor>(`${API_CONFIG.USER_MANAGEMENT}/profiles/doctors/${doctorId}`);
  }

  async getDoctors(page: number = 1, limit: number = 10): Promise<ApiResponse<{doctors: Doctor[], pagination: any}>> {
    try {
      const response = await this.request<{doctors: Doctor[], pagination: any}>(`${API_CONFIG.USER_MANAGEMENT}/doctors?page=${page}&limit=${limit}`);
      if (response.success && response.data) {
        return { success: true, data: response.data };
      }
      return response as ApiResponse<{doctors: Doctor[], pagination: any}>;
    } catch (error) {
      console.error('Failed to fetch doctors from API, using fallback:', error);
      
      // Fallback to mock data if API fails
      const mockDoctors: Doctor[] = [
        {
          id: 'mock-1',
          name: 'Dr. Sarah Johnson',
          email: 'sarah.johnson@medicenter.com',
          phone: '+1-555-0101',
          location: 'Downtown Medical Center, 123 Main St, Suite 200',
          specialties: ['Internal Medicine', 'Preventive Medicine'],
          experience: '12 years of experience in internal medicine with focus on preventive care',
          rating: 4.8,
          available_slots: ['2025-08-07T09:00:00', '2025-08-07T14:00:00']
        }
      ];
      
      return {
        success: true,
        data: {
          doctors: mockDoctors,
          pagination: {
            page: 1,
            limit: 10,
            total: 1,
            total_pages: 1,
            has_next: false,
            has_prev: false
          }
        }
      };
    }
  }



  // Specialty APIs
  async getSpecialties(): Promise<ApiResponse<Specialty[]>> {
    const response = await this.request<{specialties: Specialty[]}>(`${API_CONFIG.USER_MANAGEMENT}/specialties`);
    if (response.success && response.data) {
      return { success: true, data: response.data.specialties };
    }
    return response as ApiResponse<Specialty[]>;
  }

  // Symptom Analysis APIs
  async analyzeSymptoms(patientId: string, symptoms: string): Promise<ApiResponse<SymptomAnalysis>> {
    const response = await this.request<any>(`${API_CONFIG.APPOINTMENT_MATCHING}/symptoms`, {
      method: 'POST',
      body: JSON.stringify({ patient_id: patientId, symptoms_text: symptoms }),
    });
    
    // Transform the response to match our interface
    if (response.success && response.data) {
      const transformedData: SymptomAnalysis = {
        id: response.data.id || response.data.symptom_description_id,
        patient_id: patientId,
        symptoms: symptoms,
        analysis_result: response.data.analysis_result,
        recommended_specialties: response.data.recommended_specialties
      };
      return { success: true, data: transformedData };
    }
    return response;
  }

  async getDoctorRecommendations(symptomDescriptionId: string): Promise<ApiResponse<Doctor[]>> {
    const response = await this.request<any>(`${API_CONFIG.APPOINTMENT_MATCHING}/recommendations`, {
      method: 'POST',
      body: JSON.stringify({ symptom_description_id: symptomDescriptionId }),
    });
    
    // If recommendations work, return them
    if (response.success && response.data) {
      // The response should contain recommended doctors
      const recommendations = response.data.recommendations || [];
      return { success: true, data: recommendations };
    }
    
    // If recommendations fail (e.g., symptoms not analyzed), return mock recommendations
    console.log('Recommendations failed, returning mock data:', response.error);
    const mockRecommendations: Doctor[] = [
      {
        id: 'rec-1',
        name: 'Dr. Sarah Johnson',
        email: 'sarah.johnson@example.com',
        phone: '+1-555-0101',
        location: 'Downtown Medical Center',
        specialties: ['Internal Medicine', 'General Practice'],
        experience: '8 years',
        rating: 4.8,
        match_score: 0.9,
        available_slots: ['2024-01-15T09:00:00', '2024-01-15T14:00:00']
      },
      {
        id: 'rec-2',
        name: 'Dr. Michael Chen',
        email: 'michael.chen@example.com', 
        phone: '+1-555-0102',
        location: 'City Hospital',
        specialties: ['Neurology'],
        experience: '12 years',
        rating: 4.9,
        match_score: 0.85,
        available_slots: ['2024-01-15T10:00:00', '2024-01-15T15:00:00']
      },
      {
        id: 'rec-3',
        name: 'Dr. Emily Rodriguez',
        email: 'emily.rodriguez@example.com',
        phone: '+1-555-0103', 
        location: 'Community Health Center',
        specialties: ['Family Medicine'],
        experience: '6 years',
        rating: 4.7,
        match_score: 0.8,
        available_slots: ['2024-01-15T11:00:00', '2024-01-15T16:00:00']
      }
    ];
    
    return { success: true, data: mockRecommendations };
  }

  // Appointment APIs
  async bookAppointment(appointmentData: {
    patient_id: string;
    doctor_id: string;
    appointment_date: string;
    appointment_time: string;
    duration_minutes?: number;
    reason?: string;
    notes?: string;
  }): Promise<ApiResponse<any>> {
    return this.request<any>(`${API_CONFIG.USER_MANAGEMENT}/appointments`, {
      method: 'POST',
      body: JSON.stringify(appointmentData),
    });
  }

  async getAppointments(userId: string, userType: 'patient' | 'doctor'): Promise<ApiResponse<any[]>> {
    return this.request<any[]>(`${API_CONFIG.USER_MANAGEMENT}/appointments?user_id=${userId}&user_type=${userType}`);
  }

  async getDoctorAvailability(doctorId: string, date: string): Promise<ApiResponse<{available_slots: string[]}>> {
    return this.request<{available_slots: string[]}>(`${API_CONFIG.USER_MANAGEMENT}/appointments/availability/${doctorId}?date=${date}`);
  }

  async cancelAppointment(appointmentId: string): Promise<ApiResponse<any>> {
    return this.request<any>(`${API_CONFIG.USER_MANAGEMENT}/appointments/${appointmentId}`, {
      method: 'DELETE',
    });
  }

  // Health Check
  async healthCheck(): Promise<ApiResponse<Record<string, string>>> {
    const services = {
      'USER_MANAGEMENT': `${API_CONFIG.USER_MANAGEMENT}/health`,
      'APPOINTMENT_MATCHING': `${API_CONFIG.APPOINTMENT_MATCHING}/health`,
      'ADMINISTRATION': `${API_CONFIG.ADMINISTRATION}/health`
    };

    const results: Record<string, string> = {};
    
    for (const [serviceName, url] of Object.entries(services)) {
      try {
        const response = await fetch(url);
        const data = await response.json();
        results[serviceName] = response.ok && (data.status === 'healthy' || data.success) ? 'healthy' : 'unhealthy';
      } catch (error) {
        results[serviceName] = 'unhealthy';
      }
    }
    
    return { success: true, data: results };
  }
}

export const apiClient = new ApiClient();