import { useState, useEffect } from 'react';

interface PatientInfo {
  id: string;
  name: string;
  email: string;
  user_type: string;
}

interface PatientData {
  name: string;
  email: string;
  phone: string;
  medical_history?: string;
  emergency_contact_name: string;
  emergency_contact_phone: string;
  emergency_contact_relationship: string;
}

export const usePatientContext = () => {
  const [patientInfo, setPatientInfo] = useState<PatientInfo | null>(null);
  const [patientData, setPatientData] = useState<PatientData | null>(null);
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  useEffect(() => {
    // Load patient information from localStorage
    const storedUser = localStorage.getItem('user');
    const storedPatientData = localStorage.getItem('patientRegistrationData');

    if (storedUser) {
      try {
        const user = JSON.parse(storedUser);
        setPatientInfo(user);
        setIsLoggedIn(true);
      } catch (error) {
        console.error('Error parsing stored user data:', error);
      }
    }

    if (storedPatientData) {
      try {
        const data = JSON.parse(storedPatientData);
        setPatientData(data);
      } catch (error) {
        console.error('Error parsing stored patient data:', error);
      }
    }
  }, []);

  const clearPatientContext = () => {
    localStorage.removeItem('user');
    localStorage.removeItem('userType');
    localStorage.removeItem('patientRegistrationData');
    localStorage.removeItem('symptomAnalysis');
    setPatientInfo(null);
    setPatientData(null);
    setIsLoggedIn(false);
  };

  const updatePatientInfo = (info: PatientInfo) => {
    setPatientInfo(info);
    localStorage.setItem('user', JSON.stringify(info));
    setIsLoggedIn(true);
  };

  const updatePatientData = (data: PatientData) => {
    setPatientData(data);
    localStorage.setItem('patientRegistrationData', JSON.stringify(data));
  };

  return {
    patientInfo,
    patientData,
    isLoggedIn,
    clearPatientContext,
    updatePatientInfo,
    updatePatientData,
  };
};

export default usePatientContext;