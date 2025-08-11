import { Card, CardContent } from "@/components/ui/card";
import { User } from "lucide-react";

interface PatientInfoCardProps {
  patientInfo: {
    id: string;
    name: string;
    email: string;
  };
  message?: string;
  className?: string;
}

const PatientInfoCard = ({ 
  patientInfo, 
  message = "Logged in as:", 
  className = "mb-6 bg-green-50 border-green-200" 
}: PatientInfoCardProps) => {
  return (
    <Card className={className}>
      <CardContent className="pt-4">
        <div className="flex items-center space-x-3">
          <User className="h-5 w-5 text-green-600" />
          <div>
            <p className="text-sm font-medium text-green-800">{message}</p>
            <p className="text-green-900 font-semibold">{patientInfo.name}</p>
            <p className="text-sm text-green-700">{patientInfo.email}</p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default PatientInfoCard;