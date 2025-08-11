# HealMatch Easy - Modern Frontend

A modern React/TypeScript frontend application replicating the design and functionality from the external project, integrated with your existing AWS backend services.

## 🚀 Features

- **Modern React/TypeScript Stack** - Built with Vite, React 18, and TypeScript
- **shadcn/ui Components** - Beautiful, accessible UI components
- **Tailwind CSS** - Utility-first CSS framework for rapid styling
- **AWS Backend Integration** - Connected to your existing backend services
- **Responsive Design** - Mobile-first approach with responsive layouts
- **Patient & Doctor Flows** - Complete user journeys for both user types

## 🏗️ Architecture

- **Frontend:** React 18 + TypeScript + Vite
- **UI Components:** shadcn/ui + Radix UI primitives
- **Styling:** Tailwind CSS with custom design system
- **State Management:** React Query for server state
- **Routing:** React Router v6
- **Backend Integration:** Your existing AWS Lambda services

## 📁 Project Structure

```
new-frontend/
├── src/
│   ├── components/
│   │   └── ui/              # shadcn/ui components
│   ├── pages/               # Page components
│   │   ├── Index.tsx        # Landing page
│   │   ├── PatientRegistration.tsx
│   │   ├── DoctorRegistration.tsx
│   │   ├── SymptomInput.tsx
│   │   ├── DoctorRecommendations.tsx
│   │   ├── AppointmentBooking.tsx
│   │   ├── AppointmentConfirmation.tsx
│   │   ├── PatientDashboard.tsx
│   │   ├── DoctorDashboard.tsx
│   │   └── NotFound.tsx
│   ├── lib/
│   │   ├── api.ts           # API client and types
│   │   └── utils.ts         # Utility functions
│   ├── hooks/
│   │   └── use-toast.ts     # Toast hook
│   ├── App.tsx              # Main app component
│   ├── main.tsx             # Entry point
│   └── index.css            # Global styles
├── package.json
├── vite.config.ts
├── tailwind.config.ts
└── tsconfig.json
```

## 🔧 Backend Integration

The frontend is configured to work with your existing AWS backend services:

### API Endpoints
- **User Management:** `https://9gip0hh7mb.execute-api.us-east-1.amazonaws.com/prod/api`
- **Appointment Matching:** `https://7ljuyzkjsd.execute-api.us-east-1.amazonaws.com/prod`
- **Administration:** `https://06i3sudebb.execute-api.us-east-1.amazonaws.com/prod/api`

### API Client Features
- Patient and doctor registration
- Specialty management
- Symptom analysis
- Doctor recommendations
- Appointment booking
- Health checks

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ 
- npm or yarn

### Installation

1. **Navigate to the new frontend directory:**
   ```bash
   cd new-frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start development server:**
   ```bash
   npm run dev
   ```

4. **Open browser:**
   ```
   http://localhost:3000
   ```

### Build for Production

1. **Build optimized version:**
   ```bash
   npm run build
   ```

2. **Preview production build:**
   ```bash
   npm run preview
   ```

## 🎨 User Flows

### Patient Journey
1. **Landing Page** → Select "I'm a Patient"
2. **Patient Registration** → Enter personal and medical information
3. **Symptom Input** → Describe symptoms in detail
4. **Doctor Recommendations** → View matched doctors
5. **Appointment Booking** → Select time and confirm
6. **Appointment Confirmation** → View booking details
7. **Patient Dashboard** → Manage appointments

### Doctor Journey
1. **Landing Page** → Select "I'm a Doctor"
2. **Doctor Registration** → Enter professional information
3. **Doctor Dashboard** → Manage practice and appointments

## 🔌 API Integration Examples

### Register a Patient
```typescript
const patientData = {
  name: "Jane Doe",
  email: "jane@example.com",
  phone: "+1234567890",
  date_of_birth: "1990-01-01",
  address: "123 Main St, City, State",
  medical_history: "No significant history",
  emergency_contact_name: "John Doe",
  emergency_contact_phone: "+1234567891",
  emergency_contact_relationship: "Spouse"
};

const result = await apiClient.registerPatient(patientData);
```

### Analyze Symptoms
```typescript
const symptoms = "I have chest pain and shortness of breath";
const analysis = await apiClient.analyzeSymptoms(patientId, symptoms);
```

### Get Doctor Recommendations
```typescript
const recommendations = await apiClient.getDoctorRecommendations(analysisId);
```

## 🎨 Design System

The application uses a custom design system built on Tailwind CSS:

### Colors
- **Primary:** Blue (#2563eb) - Medical trust and professionalism
- **Secondary:** Green (#16a34a) - Health and wellness
- **Success:** Green variants for confirmations
- **Warning:** Amber for alerts
- **Error:** Red for errors

### Typography
- **Font Family:** System fonts for optimal performance
- **Headings:** Bold, clear hierarchy
- **Body Text:** Readable, accessible contrast

### Components
- **Cards:** Clean, shadowed containers
- **Buttons:** Consistent styling with hover states
- **Forms:** Clear labels, validation states
- **Navigation:** Intuitive, responsive

## 📱 Responsive Design

The application is fully responsive:
- **Desktop:** Full-featured interface (1024px+)
- **Tablet:** Touch-optimized layout (768px - 1023px)
- **Mobile:** Mobile-first design (320px - 767px)

## 🧪 Development

### Available Scripts
- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

### Adding New Components
1. Create component in appropriate directory
2. Export from index file if needed
3. Add to routing if it's a page
4. Update types in `lib/api.ts` if needed

### Styling Guidelines
- Use Tailwind utility classes
- Follow the established design system
- Ensure responsive design
- Maintain accessibility standards

## 🔒 Security Features

- **Input Sanitization** - All user inputs are validated
- **API Error Handling** - Graceful error handling
- **Session Management** - Local storage for user sessions
- **HTTPS Only** - All API calls use HTTPS

## 📊 Performance

- **Bundle Size** - Optimized with Vite
- **Code Splitting** - Route-based lazy loading
- **Tree Shaking** - Unused code elimination
- **Asset Optimization** - Optimized images and fonts

## 🌐 Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## 🚀 Deployment

### Option 1: AWS S3 + CloudFront (Recommended)
1. Build the application: `npm run build`
2. Upload `dist/` folder to S3 bucket
3. Configure CloudFront distribution
4. Update DNS records

### Option 2: Vercel/Netlify
1. Connect your repository
2. Set build command: `npm run build`
3. Set publish directory: `dist`
4. Deploy automatically on push

## 🔧 Configuration

### Environment Variables
Create `.env` file for environment-specific settings:
```
VITE_API_USER_MANAGEMENT=your-user-management-api
VITE_API_APPOINTMENT_MATCHING=your-appointment-matching-api
VITE_API_ADMINISTRATION=your-administration-api
```

### API Configuration
Update `src/lib/api.ts` to modify API endpoints or add new services.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

- Check the code comments for implementation details
- Review the API client in `src/lib/api.ts`
- Test with your backend services
- Monitor browser console for errors

---

**Ready to provide modern healthcare matching!** 🏥✨