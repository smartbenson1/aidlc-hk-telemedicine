import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { ArrowLeft, Stethoscope, Star, MapPin, Clock } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { toast } from "sonner";
import { apiClient, Doctor } from "@/lib/api";
import usePatientContext from "@/hooks/usePatientContext";
import PatientInfoCard from "@/components/PatientInfoCard";

const DoctorRecommendations = () => {
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(true);
  const [doctors, setDoctors] = useState<Doctor[]>([]);
  const [pagination, setPagination] = useState({
    page: 1,
    limit: 10,
    total: 0,
    total_pages: 1,
    has_next: false,
    has_prev: false
  });
  const { patientInfo, isLoggedIn } = usePatientContext();

  useEffect(() => {
    loadRecommendations();
  }, []);

  useEffect(() => {
    loadRecommendations();
  }, []);

  const loadRecommendations = async (page: number = 1) => {
    try {
      const analysisData = localStorage.getItem('symptomAnalysis');
      
      if (!analysisData) {
        console.log('No symptom analysis found in localStorage');
        // Instead of redirecting immediately, show fallback doctors with pagination
        console.log('Loading all available doctors with pagination');
        const fallbackResponse = await apiClient.getDoctors(page, 10);
        if (fallbackResponse.success && fallbackResponse.data) {
          setDoctors(fallbackResponse.data.doctors);
          setPagination(fallbackResponse.data.pagination);
          toast.info("Showing all available doctors. For personalized recommendations, please describe your symptoms first.");
        }
        return;
      }

      const analysis = JSON.parse(analysisData);
      console.log('Symptom analysis data:', analysis);
      
      const response = await apiClient.getDoctorRecommendations(analysis.id);
      console.log('Recommendations response:', response);
      
      if (response.success && response.data) {
        // The recommendations response should contain doctor data directly
        const recommendedDoctors = response.data;
        
        if (Array.isArray(recommendedDoctors) && recommendedDoctors.length > 0) {
          setDoctors(recommendedDoctors);
        } else {
          // If no recommendations, show fallback doctors with pagination
          console.log('No recommendations found, showing all available doctors');
          const fallbackResponse = await apiClient.getDoctors(page, 10);
          if (fallbackResponse.success && fallbackResponse.data) {
            setDoctors(fallbackResponse.data.doctors);
            setPagination(fallbackResponse.data.pagination);
          }
        }
      } else {
        console.log('Recommendations failed, showing all available doctors');
        // Fallback to all available doctors if recommendations fail
        const fallbackResponse = await apiClient.getDoctors(page, 10);
        if (fallbackResponse.success && fallbackResponse.data) {
          setDoctors(fallbackResponse.data.doctors);
          setPagination(fallbackResponse.data.pagination);
        }
      }
    } catch (error) {
      console.error('Failed to load recommendations:', error);
      toast.error("Failed to load doctor recommendations");
      
      // Even on error, show all available doctors so the user can continue
      const fallbackResponse = await apiClient.getDoctors(page, 10);
      if (fallbackResponse.success && fallbackResponse.data) {
        setDoctors(fallbackResponse.data.doctors);
        setPagination(fallbackResponse.data.pagination);
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleBookAppointment = (doctor: Doctor) => {
    navigate('/book-appointment', { state: { doctor } });
  };

  const handlePageChange = async (newPage: number) => {
    if (newPage < 1 || newPage > pagination.total_pages) return;
    
    setIsLoading(true);
    await loadRecommendations(newPage);
    setIsLoading(false);
    
    // Scroll to top of doctors list
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-white flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Finding the best doctors for you...</p>
        </div>
      </div>
    );
  }

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
              onClick={() => navigate('/symptom-input')}
              className="flex items-center space-x-2"
            >
              <ArrowLeft className="h-4 w-4" />
              <span>Back to Symptoms</span>
            </Button>
          </div>
        </div>
      </header>

      {/* Doctor Recommendations */}
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Patient Info Card */}
        {isLoggedIn && patientInfo && (
          <PatientInfoCard 
            patientInfo={patientInfo} 
            message="Finding doctors for:" 
          />
        )}

        <div className="text-center mb-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            {localStorage.getItem('symptomAnalysis') ? 'Recommended Doctors' : 'Available Doctors'}
          </h2>
          <p className="text-lg text-gray-600">
            {localStorage.getItem('symptomAnalysis') 
              ? 'Based on your symptoms, here are the best matching specialists'
              : 'Browse our network of qualified medical specialists'
            }
          </p>
        </div>

        {doctors.length === 0 ? (
          <Card className="text-center py-12">
            <CardContent>
              <p className="text-gray-600 mb-4">No doctors found matching your symptoms.</p>
              <Button onClick={() => navigate('/symptom-input')}>
                Try Different Symptoms
              </Button>
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-6">
            {doctors.map((doctor) => (
              <Card key={doctor.id} className="shadow-md hover:shadow-lg transition-shadow">
                <CardContent className="p-6">
                  <div className="flex flex-col md:flex-row md:items-center md:justify-between">
                    <div className="flex-1">
                      <div className="flex items-start justify-between mb-4">
                        <div>
                          <h3 className="text-xl font-semibold text-gray-900">{doctor.name}</h3>
                          <p className="text-blue-600 font-medium">
                            {doctor.specialty_name || (doctor.specialties && doctor.specialties.length > 0 ? doctor.specialties.join(', ') : 'Specialist')}
                          </p>
                          {doctor.match_score && (
                            <p className="text-green-600 text-sm font-medium">
                              {Math.round(doctor.match_score * 100)}% match for your symptoms
                            </p>
                          )}
                        </div>
                        <div className="flex items-center space-x-1 text-yellow-500">
                          <Star className="h-4 w-4 fill-current" />
                          <span className="text-sm font-medium text-gray-900">
                            {doctor.rating || '4.8'}
                          </span>
                        </div>
                      </div>

                      <div className="space-y-2 text-sm text-gray-600 mb-4">
                        <div className="flex items-center space-x-2">
                          <Clock className="h-4 w-4" />
                          <span>{doctor.experience || doctor.years_of_experience || 'Experience not specified'}</span>
                        </div>
                        <div className="flex items-center space-x-2">
                          <MapPin className="h-4 w-4" />
                          <span>{doctor.location || doctor.clinic_address || 'Location not specified'}</span>
                        </div>
                      </div>

                      {doctor.bio && (
                        <p className="text-gray-600 text-sm mb-4 line-clamp-2">
                          {doctor.bio}
                        </p>
                      )}
                    </div>

                    <div className="md:ml-6 mt-4 md:mt-0">
                      <Button
                        onClick={() => handleBookAppointment(doctor)}
                        className="w-full md:w-auto bg-blue-600 hover:bg-blue-700 text-white"
                      >
                        Book Appointment
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}

            {/* Pagination Controls */}
            {pagination.total_pages > 1 && (
              <div className="flex items-center justify-between mt-8 p-4 bg-white rounded-lg shadow-sm">
                <div className="text-sm text-gray-600">
                  Showing {((pagination.page - 1) * pagination.limit) + 1} to {Math.min(pagination.page * pagination.limit, pagination.total)} of {pagination.total} doctors
                </div>
                
                <div className="flex items-center space-x-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handlePageChange(pagination.page - 1)}
                    disabled={!pagination.has_prev || isLoading}
                    className="flex items-center space-x-1"
                  >
                    <ArrowLeft className="h-4 w-4" />
                    <span>Previous</span>
                  </Button>
                  
                  <div className="flex items-center space-x-1">
                    {Array.from({ length: Math.min(5, pagination.total_pages) }, (_, i) => {
                      let pageNum;
                      if (pagination.total_pages <= 5) {
                        pageNum = i + 1;
                      } else if (pagination.page <= 3) {
                        pageNum = i + 1;
                      } else if (pagination.page >= pagination.total_pages - 2) {
                        pageNum = pagination.total_pages - 4 + i;
                      } else {
                        pageNum = pagination.page - 2 + i;
                      }
                      
                      return (
                        <Button
                          key={pageNum}
                          variant={pageNum === pagination.page ? "default" : "outline"}
                          size="sm"
                          onClick={() => handlePageChange(pageNum)}
                          disabled={isLoading}
                          className="w-8 h-8 p-0"
                        >
                          {pageNum}
                        </Button>
                      );
                    })}
                  </div>
                  
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handlePageChange(pagination.page + 1)}
                    disabled={!pagination.has_next || isLoading}
                    className="flex items-center space-x-1"
                  >
                    <span>Next</span>
                    <ArrowLeft className="h-4 w-4 rotate-180" />
                  </Button>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default DoctorRecommendations;