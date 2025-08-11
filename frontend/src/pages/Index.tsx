import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Calendar, Clock, UserCheck, Stethoscope, Heart, Shield } from "lucide-react";
import { useNavigate } from "react-router-dom";

const Index = () => {
  const navigate = useNavigate();
  const [userType, setUserType] = useState<"patient" | "doctor" | null>(null);
  
  const features = [
    {
      icon: UserCheck,
      title: "Expert Matching",
      description: "AI-powered system matches you with the right medical specialist based on your symptoms and needs."
    },
    {
      icon: Calendar,
      title: "Easy Scheduling",
      description: "Book appointments instantly with real-time availability from verified healthcare professionals."
    },
    {
      icon: Clock,
      title: "Save Time",
      description: "Skip the wait. Find and book appointments with specialists faster than traditional methods."
    },
    {
      icon: Shield,
      title: "Verified Doctors",
      description: "All medical professionals are thoroughly verified and registered with proper credentials."
    }
  ];

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
            <nav className="hidden md:flex space-x-8">
              <a href="#features" className="text-gray-600 hover:text-blue-600 transition-colors">Features</a>
              <a href="#how-it-works" className="text-gray-600 hover:text-blue-600 transition-colors">How It Works</a>
              <a href="#about" className="text-gray-600 hover:text-blue-600 transition-colors">About</a>
            </nav>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="text-center mb-16">
          <h2 className="text-5xl font-bold text-gray-900 mb-6">
            Connect with the Right Doctor,
            <span className="text-blue-600 block">Faster Than Ever</span>
          </h2>
          <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
            Our AI-powered platform matches patients with medical specialists based on symptoms and availability,
            making healthcare more accessible and efficient for everyone.
          </p>
          
          {/* User Type Selection */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-8">
            <Card className={`w-64 cursor-pointer transition-all hover:shadow-lg ${userType === 'patient' ? 'ring-2 ring-blue-500 bg-blue-50' : ''}`}
                  onClick={() => setUserType('patient')}>
              <CardContent className="p-6 text-center">
                <Heart className="h-12 w-12 text-blue-600 mx-auto mb-4" />
                <h3 className="text-lg font-semibold mb-2">I'm a Patient</h3>
                <p className="text-gray-600 text-sm">Book appointments with specialists</p>
              </CardContent>
            </Card>
            
            <div className="text-gray-400 text-lg font-medium">OR</div>
            
            <Card className={`w-64 cursor-pointer transition-all hover:shadow-lg ${userType === 'doctor' ? 'ring-2 ring-blue-500 bg-blue-50' : ''}`}
                  onClick={() => setUserType('doctor')}>
              <CardContent className="p-6 text-center">
                <Stethoscope className="h-12 w-12 text-blue-600 mx-auto mb-4" />
                <h3 className="text-lg font-semibold mb-2">I'm a Doctor</h3>
                <p className="text-gray-600 text-sm">Register and manage appointments</p>
              </CardContent>
            </Card>
          </div>

          {userType && (
            <div className="animate-in slide-in-from-bottom-4 duration-500 space-y-4">
              <div>
                <Button 
                  size="lg" 
                  className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-3 text-lg"
                  onClick={() => navigate(userType === 'patient' ? '/patient-registration' : '/doctor-registration')}
                >
                  {userType === 'patient' ? 'Find a Doctor' : 'Join as Doctor'}
                </Button>
              </div>
              {userType === 'patient' && (
                <div>
                  <Button 
                    size="lg" 
                    variant="outline"
                    className="border-blue-600 text-blue-600 hover:bg-blue-50 px-8 py-3 text-lg"
                    onClick={() => navigate('/doctor-recommendations')}
                  >
                    Browse All Doctors
                  </Button>
                </div>
              )}
            </div>
          )}
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="bg-white py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h3 className="text-3xl font-bold text-gray-900 mb-4">Why Choose HealMatch Easy?</h3>
            <p className="text-lg text-gray-600">Modern healthcare deserves modern solutions</p>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {features.map((feature, index) => (
              <Card key={index} className="border-none shadow-md hover:shadow-lg transition-shadow">
                <CardContent className="p-6 text-center">
                  <feature.icon className="h-12 w-12 text-blue-600 mx-auto mb-4" />
                  <h4 className="text-lg font-semibold mb-2">{feature.title}</h4>
                  <p className="text-gray-600">{feature.description}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section id="how-it-works" className="py-16 bg-gradient-to-br from-blue-50 to-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h3 className="text-3xl font-bold text-gray-900 mb-4">How It Works</h3>
            <p className="text-lg text-gray-600">Simple steps to better healthcare</p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="w-16 h-16 bg-blue-600 text-white rounded-full flex items-center justify-center text-2xl font-bold mx-auto mb-4">1</div>
              <h4 className="text-lg font-semibold mb-2">Describe Your Symptoms</h4>
              <p className="text-gray-600">Tell us about your health concerns and symptoms in detail</p>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 bg-blue-600 text-white rounded-full flex items-center justify-center text-2xl font-bold mx-auto mb-4">2</div>
              <h4 className="text-lg font-semibold mb-2">Get Matched</h4>
              <p className="text-gray-600">Our AI matches you with the most suitable specialists</p>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 bg-blue-600 text-white rounded-full flex items-center justify-center text-2xl font-bold mx-auto mb-4">3</div>
              <h4 className="text-lg font-semibold mb-2">Book & Meet</h4>
              <p className="text-gray-600">Choose your preferred doctor and book an appointment instantly</p>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <div className="flex items-center justify-center space-x-2 mb-4">
              <Stethoscope className="h-8 w-8 text-blue-400" />
              <h4 className="text-2xl font-bold">HealMatch Easy</h4>
            </div>
            <p className="text-gray-400 mb-8">Connecting patients with the right medical specialists</p>
            <div className="flex justify-center space-x-8">
              <a href="#" className="text-gray-400 hover:text-white transition-colors">Privacy Policy</a>
              <a href="#" className="text-gray-400 hover:text-white transition-colors">Terms of Service</a>
              <a href="#" className="text-gray-400 hover:text-white transition-colors">Contact Us</a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Index;