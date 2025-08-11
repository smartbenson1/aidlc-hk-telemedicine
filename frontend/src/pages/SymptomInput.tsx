import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { ArrowLeft, Stethoscope, Search } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { toast } from "sonner";
import { apiClient } from "@/lib/api";
import usePatientContext from "@/hooks/usePatientContext";
import PatientInfoCard from "@/components/PatientInfoCard";

const SymptomInput = () => {
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false);
  const [symptoms, setSymptoms] = useState("");
  const { patientInfo, isLoggedIn } = usePatientContext();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!symptoms.trim()) {
      toast.error("Please describe your symptoms");
      return;
    }

    setIsLoading(true);

    try {
      // Check if user is logged in, if not, allow them to continue with a temporary ID
      let patientId = patientInfo?.id;
      
      if (!patientId) {
        // If no patient ID, check if we can proceed without registration
        // or create a temporary patient ID for the session
        patientId = `temp_patient_${Date.now()}`;
        console.log('No patient ID found, using temporary ID:', patientId);
      }

      const response = await apiClient.analyzeSymptoms(patientId, symptoms);
      
      if (response.success && response.data) {
        // Store analysis result for next step
        localStorage.setItem('symptomAnalysis', JSON.stringify(response.data));
        toast.success("Symptoms analyzed successfully!");
        navigate('/doctor-recommendations');
      } else {
        toast.error(response.error || "Failed to analyze symptoms. Please try again.");
      }
    } catch (error) {
      console.error('Symptom analysis error:', error);
      toast.error("Failed to analyze symptoms. Please try again.");
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

      {/* Symptom Input Form */}
      <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Patient Info Card */}
        {isLoggedIn && patientInfo && (
          <PatientInfoCard 
            patientInfo={patientInfo} 
            message="Analyzing symptoms for:" 
          />
        )}

        <Card className="shadow-lg">
          <CardHeader className="text-center">
            <div className="flex justify-center mb-4">
              <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center">
                <Search className="h-8 w-8 text-blue-600" />
              </div>
            </div>
            <CardTitle className="text-2xl">Describe Your Symptoms</CardTitle>
            <CardDescription>
              Tell us about your health concerns in detail. The more information you provide, 
              the better we can match you with the right specialist.
            </CardDescription>
          </CardHeader>
          
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="space-y-2">
                <Label htmlFor="symptoms">What symptoms are you experiencing? *</Label>
                <Textarea
                  id="symptoms"
                  value={symptoms}
                  onChange={(e) => setSymptoms(e.target.value)}
                  placeholder="Please describe your symptoms in detail. Include:
• What symptoms you're experiencing
• When they started
• How severe they are (1-10 scale)
• What makes them better or worse
• Any other relevant information

Example: 'I've been experiencing chest pain for the past 3 days. The pain is sharp and occurs mainly when I take deep breaths. It's about a 6/10 in severity and seems to get worse when I lie down. I also have some shortness of breath during physical activity.'"
                  rows={12}
                  className="resize-none"
                  required
                />
                <p className="text-sm text-gray-500">
                  Character count: {symptoms.length}/1000
                </p>
              </div>

              {/* Tips Section */}
              <Card className="bg-blue-50 border-blue-200">
                <CardContent className="p-4">
                  <h4 className="font-semibold text-blue-900 mb-2">💡 Tips for better matching:</h4>
                  <ul className="text-sm text-blue-800 space-y-1">
                    <li>• Be specific about the location and type of pain or discomfort</li>
                    <li>• Mention how long you've had these symptoms</li>
                    <li>• Include any triggers or patterns you've noticed</li>
                    <li>• Note any medications you're currently taking</li>
                    <li>• Mention if you have any relevant medical history</li>
                  </ul>
                </CardContent>
              </Card>

              <Button
                type="submit"
                className="w-full bg-blue-600 hover:bg-blue-700 text-white py-3"
                disabled={isLoading || symptoms.length === 0}
              >
                {isLoading ? "Analyzing Symptoms..." : "Find Matching Doctors"}
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default SymptomInput;