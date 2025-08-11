import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Stethoscope, Calendar, User, Plus } from "lucide-react";
import { useNavigate } from "react-router-dom";

const PatientDashboard = () => {
  const navigate = useNavigate();

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
              <span className="text-gray-600">Welcome back!</span>
              <Button
                onClick={() => navigate('/')}
                variant="outline"
              >
                Logout
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Dashboard */}
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-2">Patient Dashboard</h2>
          <p className="text-gray-600">Manage your appointments and health information</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Quick Actions */}
          <div className="lg:col-span-1">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Plus className="h-5 w-5" />
                  <span>Quick Actions</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <Button
                  onClick={() => navigate('/symptom-input')}
                  className="w-full bg-blue-600 hover:bg-blue-700 text-white"
                >
                  Find a Doctor
                </Button>
                <Button
                  onClick={() => navigate('/patient-registration')}
                  variant="outline"
                  className="w-full"
                >
                  Update Profile
                </Button>
              </CardContent>
            </Card>
          </div>

          {/* Appointments */}
          <div className="lg:col-span-2">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Calendar className="h-5 w-5" />
                  <span>My Appointments</span>
                </CardTitle>
                <CardDescription>
                  Your upcoming and past appointments
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-center py-12">
                  <Calendar className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-600 mb-4">No appointments scheduled</p>
                  <Button
                    onClick={() => navigate('/symptom-input')}
                    className="bg-blue-600 hover:bg-blue-700 text-white"
                  >
                    Book Your First Appointment
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PatientDashboard;