import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { ArrowLeft, Stethoscope, User } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { toast } from "sonner";
import { apiClient } from "@/lib/api";
import usePatientContext from "@/hooks/usePatientContext";

const PatientRegistration = () => {
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false);
  const { updatePatientInfo, updatePatientData } = usePatientContext();
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    phone: "",
    medical_history: "",
    emergency_contact_name: "",
    emergency_contact_phone: "",
    emergency_contact_relationship: ""
  });

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      const response = await apiClient.registerPatient(formData);
      
      if (response.success && response.data) {
        toast.success("Registration successful! Welcome to HealMatch Easy.");
        
        // Update patient context with user info and registration data
        const userData = {
          id: response.data.user_id,
          name: response.data.name,
          email: response.data.email,
          user_type: response.data.user_type
        };
        
        updatePatientInfo(userData);
        updatePatientData(formData);
        localStorage.setItem('userType', 'patient');
        
        navigate('/symptom-input');
      } else {
        toast.error(response.error || "Registration failed. Please try again.");
      }
    } catch (error) {
      console.error('Registration error:', error);
      toast.error("Registration failed. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

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
            <Button
              variant="ghost"
              onClick={() => navigate('/')}
              className="flex items-center space-x-2"
            >
              <ArrowLeft className="h-4 w-4" />
              <span>Back to Home</span>
            </Button>
          </div>
        </div>
      </header>

      {/* Registration Form */}
      <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <Card className="shadow-lg">
          <CardHeader className="text-center">
            <div className="flex justify-center mb-4">
              <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center">
                <User className="h-8 w-8 text-blue-600" />
              </div>
            </div>
            <CardTitle className="text-2xl">Patient Registration</CardTitle>
            <CardDescription>
              Create your account to find the right medical care
            </CardDescription>
          </CardHeader>
          
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Personal Information */}
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-gray-900">Personal Information</h3>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="name">Full Name *</Label>
                    <Input
                      id="name"
                      name="name"
                      type="text"
                      required
                      value={formData.name}
                      onChange={handleInputChange}
                      placeholder="Enter your full name"
                    />
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="email">Email Address *</Label>
                    <Input
                      id="email"
                      name="email"
                      type="email"
                      required
                      value={formData.email}
                      onChange={handleInputChange}
                      placeholder="Enter your email"
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="phone">Phone Number *</Label>
                  <Input
                    id="phone"
                    name="phone"
                    type="tel"
                    required
                    value={formData.phone}
                    onChange={handleInputChange}
                    placeholder="Enter your phone number"
                  />
                </div>
              </div>

              {/* Medical Information */}
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-gray-900">Medical Information</h3>
                
                <div className="space-y-2">
                  <Label htmlFor="medical_history">Medical History (Optional)</Label>
                  <Textarea
                    id="medical_history"
                    name="medical_history"
                    value={formData.medical_history}
                    onChange={handleInputChange}
                    placeholder="Please describe any relevant medical history, allergies, or current medications"
                    rows={4}
                  />
                </div>
              </div>

              {/* Emergency Contact */}
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-gray-900">Emergency Contact</h3>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="emergency_contact_name">Contact Name *</Label>
                    <Input
                      id="emergency_contact_name"
                      name="emergency_contact_name"
                      type="text"
                      required
                      value={formData.emergency_contact_name}
                      onChange={handleInputChange}
                      placeholder="Emergency contact name"
                    />
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="emergency_contact_phone">Contact Phone *</Label>
                    <Input
                      id="emergency_contact_phone"
                      name="emergency_contact_phone"
                      type="tel"
                      required
                      value={formData.emergency_contact_phone}
                      onChange={handleInputChange}
                      placeholder="Emergency contact phone"
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="emergency_contact_relationship">Relationship *</Label>
                  <Input
                    id="emergency_contact_relationship"
                    name="emergency_contact_relationship"
                    type="text"
                    required
                    value={formData.emergency_contact_relationship}
                    onChange={handleInputChange}
                    placeholder="e.g., Spouse, Parent, Sibling"
                  />
                </div>
              </div>

              <Button
                type="submit"
                className="w-full bg-blue-600 hover:bg-blue-700 text-white py-3"
                disabled={isLoading}
              >
                {isLoading ? "Creating Account..." : "Create Account"}
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default PatientRegistration;