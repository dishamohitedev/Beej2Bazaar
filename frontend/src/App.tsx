import React from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
import { LoginPage } from './pages/Auth/LoginPage';
import { OnboardingPage } from './pages/Onboarding/OnboardingPage';
import { DashboardPage } from './pages/Dashboard/DashboardPage';
import { Loader2, Sprout } from 'lucide-react';

const RootAppContent: React.FC = () => {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen bg-[#F7FAF4] flex flex-col items-center justify-center gap-3">
        <div className="h-12 w-12 bg-[#2E7D32]/10 rounded-2xl flex items-center justify-center text-[#2E7D32] animate-bounce">
          <Sprout size={24} />
        </div>
        <div className="flex items-center gap-2 text-slate-400 text-xs font-black uppercase tracking-wider">
          <Loader2 className="animate-spin text-[#2E7D32]" size={14} />
          <span>Syncing Profile...</span>
        </div>
      </div>
    );
  }

  if (!user) {
    return <LoginPage />;
  }

  if (!user.is_profile_complete) {
    return <OnboardingPage />;
  }

  return <DashboardPage />;
};

function App() {
  return (
    <AuthProvider>
      <RootAppContent />
    </AuthProvider>
  );
}

export default App;
