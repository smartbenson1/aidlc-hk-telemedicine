import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { CheckCircle, Calendar, Clock, MapPin, User, Phone, Mail } from "lucide-react";
import { useNavigate, useLocation } from "react-router-dom";

const AppointmentConfirmation = () => {
  const navigate = useNavigate();
  const location = useLocation();
  
  const { appointment, doctor, patient } = location.state || {};
  
  // Debug logging to see what data we're receiving
  console.log('Appointment confirmation data:', { appointment, doctor, patient });

  // Format date and time for display
  const formatDate = (dateStr: string) => {
    if (!dateStr) return 'Date not available';
    try {
      // Handle YYYY-MM-DD format
      const date = new Date(dateStr + 'T00:00:00');
      if (isNaN(date.getTime())) {
        return dateStr; // Return original string if parsing fails
      }
      return date.toLocaleDateString('en-US', { 
        weekday: 'long', 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric' 
      });
    } catch (error) {
      console.error('Error formatting date:', error);
      return dateStr; // Return original string if error occurs
    }
  };

  const formatTime = (timeStr: string) => {
    if (!timeStr) return 'Time not available';
    try {
      const [hours, minutes] = timeStr.split(':');
      if (!hours || !minutes) return timeStr; // Return original if format is unexpected
      
      const date = new Date();
      date.setHours(parseInt(hours), parseInt(minutes));
      return date.toLocaleTimeString('en-US', { 
        hour: 'numeric', 
        minute: '2-digit',
        hour12: true 
      });
    } catch (error) {
      console.error('Error formatting time:', error);
      return timeStr; // Return original string if error occurs
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-white">
      {/* Confirmation */}
      <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <Card className="shadow-lg">
          <CardHeader className="text-center">
            <div className="flex justify-center mb-4">
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center">
                <CheckCircle className="h-8 w-8 text-green-600" />
              </div>
            </div>
            <CardTitle className="text-2xl text-green-800">Appointment Confirmed!</CardTitle>
            <CardDescription>
              Your appointment has been successfully booked
            </CardDescription>
            {appointment?.appointment_id && (
              <p className="text-sm text-gray-600 mt-2">
                Confirmation ID: {appointment.appointment_id}
              </p>
            )}
          </CardHeader>
          
          <CardContent className="space-y-6">
            {/* Doctor Information */}
            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
              <h3 className="font-semibold text-green-800 mb-3">Doctor Information</h3>
              <div className="space-y-2 text-sm">
                <div className="flex items-center space-x-2">
                  <User className="h-4 w-4 text-green-600" />
                  <span>{doctor?.name || 'Doctor name not available'}</span>
                </div>
                {doctor?.specialties && (
                  <div className="flex items-center space-x-2">
                    <span className="h-4 w-4 text-green-600">🩺</span>
                    <span>{doctor.specialties.join(', ')}</span>
                  </div>
                )}
                {doctor?.location && (
                  <div className="flex items-center space-x-2">
                    <MapPin className="h-4 w-4 text-green-600" />
                    <span>{doctor.location}</span>
                  </div>
                )}
                {doctor?.phone && (
                  <div className="flex items-center space-x-2">
                    <Phone className="h-4 w-4 text-green-600" />
                    <span>{doctor.phone}</span>
                  </div>
                )}
              </div>
            </div>

            {/* Appointment Details */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <h3 className="font-semibold text-blue-800 mb-3">Appointment Details</h3>
              <div className="space-y-2 text-sm">
                <div className="flex items-center space-x-2">
                  <Calendar className="h-4 w-4 text-blue-600" />
                  <span>{formatDate(appointment?.appointment_date)}</span>
                </div>
                <div className="flex items-center space-x-2">
                  <Clock className="h-4 w-4 text-blue-600" />
                  <span>{formatTime(appointment?.appointment_time)} ({appointment?.duration_minutes || 30} minutes)</span>
                </div>
                {appointment?.reason && (
                  <div className="flex items-start space-x-2">
                    <span className="h-4 w-4 text-blue-600 mt-0.5">📝</span>
                    <span>Reason: {appointment.reason}</span>
                  </div>
                )}
                {appointment?.status && (
                  <div className="flex items-center space-x-2">
                    <span className="h-4 w-4 text-blue-600">✓</span>
                    <span>Status: {appointment.status}</span>
                  </div>
                )}
              </div>
            </div>

            {/* Patient Information */}
            {patient && (
              <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                <h3 className="font-semibold text-gray-800 mb-3">Patient Information</h3>
                <div className="space-y-2 text-sm">
                  <div className="flex items-center space-x-2">
                    <User className="h-4 w-4 text-gray-600" />
                    <span>{patient.name}</span>
                  </div>
                  {patient.email && (
                    <div className="flex items-center space-x-2">
                      <Mail className="h-4 w-4 text-gray-600" />
                      <span>{patient.email}</span>
                    </div>
                  )}
                  {patient.phone && (
                    <div className="flex items-center space-x-2">
                      <Phone className="h-4 w-4 text-gray-600" />
                      <span>{patient.phone}</span>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Next Steps */}
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
              <h4 className="font-semibold text-yellow-800 mb-2">What's Next?</h4>
              <ul className="text-sm text-yellow-700 space-y-1">
                <li>• You'll receive a confirmation email shortly</li>
                <li>• Arrive 15 minutes early for check-in</li>
                <li>• Bring your insurance card and ID</li>
                <li>• Prepare any questions you'd like to ask</li>
                <li>• If you need to cancel or reschedule, contact the office at least 24 hours in advance</li>
              </ul>
            </div>

            <div className="flex flex-col sm:flex-row gap-3">
              <Button
                onClick={() => navigate('/doctor-recommendations')}
                className="flex-1 bg-blue-600 hover:bg-blue-700 text-white"
              >
                Book Another Appointment
              </Button>
              <Button
                onClick={() => navigate('/')}
                variant="outline"
                className="flex-1"
              >
                Back to Home
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default AppointmentConfirmation;