import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { ArrowLeft, Stethoscope, Calendar, Clock, User, FileText } from "lucide-react";
import { useNavigate, useLocation } from "react-router-dom";
import { apiClient } from "@/lib/api";
import usePatientContext from "@/hooks/usePatientContext";
import PatientInfoCard from "@/components/PatientInfoCard";

const AppointmentBooking = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const selectedDoctor = location.state?.doctor;

  const [formData, setFormData] = useState({
    patient_name: '',
    patient_email: '',
    patient_phone: '',
    appointment_date: '',
    appointment_time: '',
    reason: '',
    notes: ''
  });

  const [availableSlots, setAvailableSlots] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [bookingLoading, setBookingLoading] = useState(false);
  const { patientInfo, patientData, isLoggedIn } = usePatientContext();

  // Pre-populate form with patient data when available
  useEffect(() => {
    if (patientInfo) {
      setFormData(prev => ({
        ...prev,
        patient_name: patientData?.name || patientInfo.name || '',
        patient_email: patientData?.email || patientInfo.email || '',
        patient_phone: patientData?.phone || ''
      }));
    }
  }, [patientInfo, patientData]);

  // Load available slots when date changes
  useEffect(() => {
    if (formData.appointment_date && selectedDoctor) {
      loadAvailableSlots();
    }
  }, [formData.appointment_date, selectedDoctor]);

  const loadAvailableSlots = async () => {
    if (!selectedDoctor || !formData.appointment_date) return;
    
    setLoading(true);
    try {
      const response = await apiClient.getDoctorAvailability(selectedDoctor.id, formData.appointment_date);
      if (response.success && response.data && response.data.available_slots) {
        setAvailableSlots(response.data.available_slots);
        console.log('Available slots loaded:', response.data.available_slots);
      } else {
        console.log('API response failed, using fallback slots:', response.error);
        // Fallback to default slots if API fails
        setAvailableSlots(['09:00', '09:30', '10:00', '10:30', '11:00', '11:30', '14:00', '14:30', '15:00', '15:30', '16:00', '16:30']);
      }
    } catch (error) {
      console.error('Error loading available slots:', error);
      // Fallback to default slots
      setAvailableSlots(['09:00', '09:30', '10:00', '10:30', '11:00', '11:30', '14:00', '14:30', '15:00', '15:30', '16:00', '16:30']);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleBookAppointment = async () => {
    if (!selectedDoctor) {
      alert('No doctor selected');
      return;
    }

    // Validate required fields
    if (!formData.patient_name || !formData.patient_email || !formData.appointment_date || !formData.appointment_time) {
      alert('Please fill in all required fields');
      return;
    }

    setBookingLoading(true);
    try {
      // Use stored patient ID if available, otherwise create a temporary one
      const patientId = patientInfo?.id || `temp_patient_${Date.now()}`;
      
      const appointmentData = {
        patient_id: patientId,
        doctor_id: selectedDoctor.id,
        appointment_date: formData.appointment_date,
        appointment_time: formData.appointment_time,
        duration_minutes: 30,
        reason: formData.reason,
        notes: `Patient: ${formData.patient_name}, Email: ${formData.patient_email}, Phone: ${formData.patient_phone}. ${formData.notes}`
      };

      const response = await apiClient.bookAppointment(appointmentData);
      
      // Debug logging
      console.log('Booking API response:', response);
      
      if (response.success) {
        // Navigate to confirmation page with appointment details
        // The backend returns the full response in response.data, and appointment details in response.data.appointment
        const bookedAppointment = response.data?.appointment;
        console.log('Full API response:', response.data);
        console.log('Extracted appointment data:', bookedAppointment);
        
        // Fallback: if appointment is not found in the expected location, create it from form data
        const appointmentToPass = bookedAppointment || {
          appointment_date: formData.appointment_date,
          appointment_time: formData.appointment_time,
          duration_minutes: 30,
          reason: formData.reason,
          status: 'scheduled',
          appointment_id: response.data?.appointment_id || 'unknown'
        };
        
        navigate('/appointment-confirmation', {
          state: {
            appointment: appointmentToPass,
            doctor: selectedDoctor,
            patient: {
              name: formData.patient_name,
              email: formData.patient_email,
              phone: formData.patient_phone
            }
          }
        });
      } else {
        alert(`Failed to book appointment: ${response.error || 'Unknown error'}`);
      }
    } catch (error) {
      console.error('Error booking appointment:', error);
      alert('Failed to book appointment. Please try again.');
    } finally {
      setBookingLoading(false);
    }
  };

  // Get minimum date (today)
  const today = new Date().toISOString().split('T')[0];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-white">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Stethoscope className="h-8 w-8 text-blue-600" />
              <h1 className="text-2xl font-bold text-gray-900">HealMatch Easy</h1>
            </div>
            <div className="flex items-center space-x-4">
              {isLoggedIn && patientInfo && (
                <span className="text-sm text-gray-600">
                  Welcome, {patientInfo.name}
                </span>
              )}
              <Button
                variant="ghost"
                onClick={() => navigate('/doctor-recommendations')}
                className="flex items-center space-x-2"
              >
                <ArrowLeft className="h-4 w-4" />
                <span>Back to Doctors</span>
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Booking Form */}
      <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <Card className="shadow-lg">
          <CardHeader className="text-center">
            <div className="flex justify-center mb-4">
              <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center">
                <Calendar className="h-8 w-8 text-blue-600" />
              </div>
            </div>
            <CardTitle className="text-2xl">Book Appointment</CardTitle>
            <CardDescription>
              {selectedDoctor ? `Schedule your appointment with ${selectedDoctor.name}` : 'Schedule your appointment'}
            </CardDescription>
          </CardHeader>
          
          <CardContent className="space-y-6">
            {/* Doctor Info */}
            {selectedDoctor && (
              <Card className="bg-blue-50 border-blue-200">
                <CardContent className="pt-4">
                  <div className="flex items-center space-x-3">
                    <User className="h-5 w-5 text-blue-600" />
                    <div>
                      <h3 className="font-semibold text-blue-900">{selectedDoctor.name}</h3>
                      <p className="text-sm text-blue-700">{selectedDoctor.specialties?.join(', ')}</p>
                      <p className="text-sm text-blue-600">{selectedDoctor.location}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Patient Information */}
            <div className="space-y-4">
              <h3 className="text-lg font-semibold flex items-center space-x-2">
                <User className="h-5 w-5" />
                <span>Patient Information</span>
              </h3>
              
              {isLoggedIn && patientInfo ? (
                // Show patient info as read-only when logged in
                <Card className="bg-green-50 border-green-200">
                  <CardContent className="pt-4">
                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium text-green-800">Booking for:</span>
                        <span className="text-sm text-green-600">✓ Logged in</span>
                      </div>
                      <div className="text-green-900">
                        <p className="font-semibold">{formData.patient_name}</p>
                        <p className="text-sm">{formData.patient_email}</p>
                        {formData.patient_phone && <p className="text-sm">{formData.patient_phone}</p>}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ) : (
                // Show input fields when not logged in
                <>
                  <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                    <p className="text-sm text-yellow-800">
                      💡 <strong>Tip:</strong> Register as a patient first to skip filling out this information every time!
                    </p>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="patient_name">Full Name *</Label>
                      <Input
                        id="patient_name"
                        value={formData.patient_name}
                        onChange={(e) => handleInputChange('patient_name', e.target.value)}
                        placeholder="Enter your full name"
                        required
                      />
                    </div>
                    
                    <div>
                      <Label htmlFor="patient_phone">Phone Number</Label>
                      <Input
                        id="patient_phone"
                        value={formData.patient_phone}
                        onChange={(e) => handleInputChange('patient_phone', e.target.value)}
                        placeholder="Enter your phone number"
                      />
                    </div>
                  </div>
                  
                  <div>
                    <Label htmlFor="patient_email">Email Address *</Label>
                    <Input
                      id="patient_email"
                      type="email"
                      value={formData.patient_email}
                      onChange={(e) => handleInputChange('patient_email', e.target.value)}
                      placeholder="Enter your email address"
                      required
                    />
                  </div>
                </>
              )}
            </div>

            {/* Appointment Scheduling */}
            <div className="space-y-4">
              <h3 className="text-lg font-semibold flex items-center space-x-2">
                <Calendar className="h-5 w-5" />
                <span>Schedule Appointment</span>
              </h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="appointment_date">Appointment Date *</Label>
                  <Input
                    id="appointment_date"
                    type="date"
                    value={formData.appointment_date}
                    onChange={(e) => handleInputChange('appointment_date', e.target.value)}
                    min={today}
                    required
                  />
                </div>
                
                <div>
                  <Label htmlFor="appointment_time">Available Time Slots *</Label>
                  <Select
                    value={formData.appointment_time}
                    onValueChange={(value) => handleInputChange('appointment_time', value)}
                    disabled={availableSlots.length === 0 || loading}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder={
                        loading ? "Loading slots..." : 
                        availableSlots.length === 0 ? "Select a date first" :
                        "Select time slot"
                      } />
                    </SelectTrigger>
                    <SelectContent>
                      {availableSlots.map((slot) => (
                        <SelectItem key={slot} value={slot}>
                          <div className="flex items-center space-x-2">
                            <Clock className="h-4 w-4" />
                            <span>{slot}</span>
                          </div>
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  {formData.appointment_date && availableSlots.length > 0 && (
                    <p className="text-sm text-green-600 mt-1">
                      ✓ {availableSlots.length} time slots available for {formData.appointment_date}
                    </p>
                  )}
                </div>
              </div>
            </div>

            {/* Appointment Details */}
            <div className="space-y-4">
              <h3 className="text-lg font-semibold flex items-center space-x-2">
                <FileText className="h-5 w-5" />
                <span>Appointment Details</span>
              </h3>
              
              <div>
                <Label htmlFor="reason">Reason for Visit</Label>
                <Input
                  id="reason"
                  value={formData.reason}
                  onChange={(e) => handleInputChange('reason', e.target.value)}
                  placeholder="Brief description of your concern"
                />
              </div>
              
              <div>
                <Label htmlFor="notes">Additional Notes</Label>
                <Textarea
                  id="notes"
                  value={formData.notes}
                  onChange={(e) => handleInputChange('notes', e.target.value)}
                  placeholder="Any additional information you'd like to share"
                  rows={3}
                />
              </div>
            </div>

            {/* Book Button */}
            <Button
              onClick={handleBookAppointment}
              disabled={bookingLoading || !formData.patient_name || !formData.patient_email || !formData.appointment_date || !formData.appointment_time}
              className="w-full"
              size="lg"
            >
              {bookingLoading ? 'Booking Appointment...' : 'Book Appointment'}
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default AppointmentBooking;