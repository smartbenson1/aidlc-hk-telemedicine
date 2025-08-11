import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { ArrowLeft, Stethoscope, UserCheck } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { toast } from "sonner";
import { apiClient, Specialty } from "@/lib/api";

const DoctorRegistration = () => {
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false);
  const [specialties, setSpecialties] = useState<Specialty[]>([]);
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    phone: "",
    location: "",
    specialties: [] as string[],
    experience: ""
  });

  useEffect(() => {
    loadSpecialties();
  }, []);

  const loadSpecialties = async () => {
    // Always use comprehensive specialties list for better user experience
    const comprehensiveSpecialties = [
        { id: "1", name: "General Practice" },
        { id: "2", name: "Internal Medicine" },
        { id: "3", name: "Cardiology" },
        { id: "4", name: "Dermatology" },
        { id: "5", name: "Emergency Medicine" },
        { id: "6", name: "Anesthesiology" },
        { id: "7", name: "Radiology" },
        { id: "8", name: "Pathology" },
        { id: "9", name: "Psychiatry" },
        { id: "10", name: "Obstetrics and Gynecology" },
        { id: "11", name: "Ophthalmology" },
        { id: "12", name: "Otolaryngology" },
        { id: "13", name: "Urology" },
        { id: "14", name: "Gastroenterology" },
        { id: "15", name: "Pulmonology" },
        { id: "16", name: "Endocrinology" },
        { id: "17", name: "Rheumatology" },
        { id: "18", name: "Hematology" },
        { id: "19", name: "Oncology" },
        { id: "20", name: "Nephrology" },
        { id: "21", name: "Infectious Disease" },
        { id: "22", name: "Allergy and Immunology" },
        { id: "23", name: "Physical Medicine" },
        { id: "24", name: "Plastic Surgery" },
        { id: "25", name: "Orthopedic Surgery" },
        { id: "26", name: "Neurosurgery" },
        { id: "27", name: "Cardiac Surgery" },
        { id: "28", name: "Thoracic Surgery" },
        { id: "29", name: "Vascular Surgery" },
        { id: "30", name: "General Surgery" },
        { id: "31", name: "Pediatric Surgery" },
        { id: "32", name: "Trauma Surgery" },
        { id: "33", name: "Pediatrics" },
        { id: "34", name: "Orthopedics" },
        { id: "35", name: "Neurology" },
        { id: "36", name: "Sports Medicine" },
        { id: "37", name: "Occupational Medicine" },
        { id: "38", name: "Preventive Medicine" },
        { id: "39", name: "Geriatrics" },
        { id: "40", name: "Palliative Care" },
        { id: "41", name: "Pain Management" },
        { id: "42", name: "Sleep Medicine" },
        { id: "43", name: "Addiction Medicine" },
        { id: "44", name: "Nuclear Medicine" },
        { id: "45", name: "Interventional Radiology" }
      ];

    setSpecialties(comprehensiveSpecialties);

    // Optional: Try to load from API for future compatibility
    try {
      const response = await apiClient.getSpecialties();
      if (response.success && response.data && response.data.length > comprehensiveSpecialties.length) {
        // Only use API data if it has more specialties than our comprehensive list
        setSpecialties(response.data);
      }
    } catch (error) {
      console.error('Failed to load specialties from API, using comprehensive list:', error);
      // Already set comprehensive list above
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSelectChange = (name: string, value: string | string[]) => {
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      // Validate that at least one specialty is selected
      if (!formData.specialties || formData.specialties.length === 0) {
        toast.error("Please select at least one medical specialty.");
        setIsLoading(false);
        return;
      }

      const doctorData = {
        name: formData.name,
        email: formData.email,
        phone: formData.phone,
        location: formData.location,
        specialties: formData.specialties, // This should be an array of UUIDs
        experience: formData.experience
      };

      const response = await apiClient.registerDoctor(doctorData);
      
      if (response.success && response.data) {
        toast.success("Registration successful! Welcome to HealMatch Easy.");
        // Store user data in localStorage for session management
        const userData = {
          id: response.data.user_id,
          name: response.data.name,
          email: response.data.email,
          user_type: response.data.user_type
        };
        localStorage.setItem('user', JSON.stringify(userData));
        localStorage.setItem('userType', 'doctor');
        navigate('/doctor-dashboard');
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
                <UserCheck className="h-8 w-8 text-blue-600" />
              </div>
            </div>
            <CardTitle className="text-2xl">Doctor Registration</CardTitle>
            <CardDescription>
              Join our network of medical professionals
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
                      placeholder="Dr. John Smith"
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
                      placeholder="doctor@example.com"
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

              {/* Professional Information */}
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-gray-900">Professional Information</h3>
                
                <div className="space-y-2">
                  <Label htmlFor="location">Practice Location *</Label>
                  <Textarea
                    id="location"
                    name="location"
                    required
                    value={formData.location}
                    onChange={handleInputChange}
                    placeholder="Enter your practice location/clinic address"
                    rows={3}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="specialties">Medical Specialties *</Label>
                  <Select
                    value={formData.specialties[0] || ""}
                    onValueChange={(value) => setFormData(prev => ({ ...prev, specialties: [value] }))}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select your primary specialty" />
                    </SelectTrigger>
                    <SelectContent>
                      {specialties.map((specialty) => (
                        <SelectItem key={specialty.id} value={specialty.id}>
                          {specialty.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="experience">Professional Experience *</Label>
                  <Textarea
                    id="experience"
                    name="experience"
                    required
                    value={formData.experience}
                    onChange={handleInputChange}
                    placeholder="Describe your professional experience, qualifications, and areas of expertise"
                    rows={4}
                  />
                </div>
              </div>

              <Button
                type="submit"
                className="w-full bg-blue-600 hover:bg-blue-700 text-white py-3"
                disabled={isLoading}
              >
                {isLoading ? "Creating Account..." : "Create Doctor Account"}
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default DoctorRegistration;