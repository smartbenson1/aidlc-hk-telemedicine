import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Index from "./pages/Index";
import DoctorRegistration from "./pages/DoctorRegistration";
import PatientRegistration from "./pages/PatientRegistration";
import SymptomInput from "./pages/SymptomInput";
import DoctorRecommendations from "./pages/DoctorRecommendations";
import AppointmentBooking from "./pages/AppointmentBooking";
import AppointmentConfirmation from "./pages/AppointmentConfirmation";
import PatientDashboard from "./pages/PatientDashboard";
import DoctorDashboard from "./pages/DoctorDashboard";
import NotFound from "./pages/NotFound";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Index />} />
          <Route path="/doctor-registration" element={<DoctorRegistration />} />
          <Route path="/patient-registration" element={<PatientRegistration />} />
          <Route path="/symptom-input" element={<SymptomInput />} />
          <Route path="/doctor-recommendations" element={<DoctorRecommendations />} />
          <Route path="/book-appointment" element={<AppointmentBooking />} />
          <Route path="/appointment-confirmation" element={<AppointmentConfirmation />} />
          <Route path="/patient-dashboard" element={<PatientDashboard />} />
          <Route path="/doctor-dashboard" element={<DoctorDashboard />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;