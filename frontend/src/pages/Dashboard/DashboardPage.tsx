import React, { useState } from 'react';
import { Header } from '../../components/layout/Header';
import { BottomNavigation } from '../../components/layout/BottomNavigation';
import { WeatherCard } from '../../components/cards/WeatherCard';
import { CurrentCropCard } from '../../components/cards/CurrentCropCard';
import { RecommendationCard } from '../../components/cards/RecommendationCard';
import { IrrigationCard } from '../../components/cards/IrrigationCard';
import { DiseaseAlertCard } from '../../components/cards/DiseaseAlertCard';
import { MarketCard } from '../../components/cards/MarketCard';
import { CommunityCard } from '../../components/cards/CommunityCard';
import { Sparkles, Droplet, Users, ArrowLeft } from 'lucide-react';
import { RecommendPage } from '../Recommend/RecommendPage';
import { IrrigationPage } from '../Irrigation/IrrigationPage';
import { 
  mockFarmerProfile, 
  mockWeatherData, 
  mockCurrentCropData, 
  mockCropSuggestions, 
  mockIrrigationData, 
  mockDiseaseAlerts, 
  mockMandiRates, 
  mockCommunityPost 
} from './mockData';

export const DashboardPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState('home');

  const renderTabContent = () => {
    switch (activeTab) {
      case 'home':
        return (
          <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
            {/* Weather Card - double span on wider screens */}
            <WeatherCard data={mockWeatherData} delay={0.05} />
            
            {/* Disease Alerts Card */}
            <DiseaseAlertCard alerts={mockDiseaseAlerts} delay={0.1} />

            {/* Current Active Crop Tracker */}
            <CurrentCropCard data={mockCurrentCropData} delay={0.15} />

            {/* Smart Irrigation Card */}
            <IrrigationCard data={mockIrrigationData} delay={0.2} />

            {/* AI Crop Recommendation suggestions */}
            <RecommendationCard suggestions={mockCropSuggestions} delay={0.25} />

            {/* Mandi Rates Card */}
            <MarketCard rates={mockMandiRates} delay={0.3} />

            {/* Community Feed Card */}
            <CommunityCard post={mockCommunityPost} delay={0.35} />
          </div>
        );
      
      case 'recommend':
        return (
          <RecommendPage onBackToDashboard={() => setActiveTab('home')} />
        );

      case 'irrigation':
        return (
          <IrrigationPage onBackToDashboard={() => setActiveTab('home')} />
        );

      case 'community':
        return (
          <div className="bg-white rounded-[24px] p-8 border border-[#2e7d32]/5 shadow-elevation max-w-lg mx-auto text-center space-y-4">
            <div className="h-12 w-12 rounded-2xl bg-purple-50 text-[#2E7D32] flex items-center justify-center mx-auto">
              <Users size={24} />
            </div>
            <h2 className="text-xl font-extrabold text-slate-800">Farmer Forum</h2>
            <p className="text-xs font-semibold text-slate-500 leading-relaxed">
              Connect with crop experts, share leaf diagnostics images, and coordinate organic harvesting circles.
            </p>
            <div className="pt-2">
              <button 
                onClick={() => setActiveTab('home')}
                className="inline-flex items-center gap-2 text-xs font-bold text-[#2E7D32] hover:underline cursor-pointer"
              >
                <ArrowLeft size={14} />
                <span>Return to Dashboard</span>
              </button>
            </div>
          </div>
        );

      case 'profile':
        return (
          <div className="bg-white rounded-[24px] p-6 border border-[#2e7d32]/5 shadow-elevation max-w-md mx-auto space-y-4">
            <div className="flex items-center gap-3">
              <div className="h-12 w-12 rounded-full bg-slate-100 flex items-center justify-center text-lg font-bold text-slate-655">
                {mockFarmerProfile.name[0]}
              </div>
              <div className="flex flex-col">
                <h3 className="text-base font-extrabold text-slate-800">{mockFarmerProfile.name}</h3>
                <span className="text-[10px] text-[#2E7D32] font-bold uppercase tracking-wider">
                  Verified Farmer Profile
                </span>
              </div>
            </div>

            <div className="border-t border-slate-100 pt-4 space-y-2.5 text-xs font-bold">
              <div className="flex justify-between">
                <span className="text-slate-400">Location</span>
                <span className="text-slate-800">{mockFarmerProfile.location}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Soil Type</span>
                <span className="text-slate-800">{mockFarmerProfile.soilType}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Farm Size</span>
                <span className="text-slate-800">{mockFarmerProfile.farmSizeAcres} Acres</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Region</span>
                <span className="text-slate-800">{mockFarmerProfile.district}, {mockFarmerProfile.state}</span>
              </div>
            </div>

            <div className="pt-4 border-t border-slate-100 text-center">
              <button 
                onClick={() => setActiveTab('home')}
                className="inline-flex items-center gap-2 text-xs font-bold text-[#2E7D32] hover:underline cursor-pointer"
              >
                <ArrowLeft size={14} />
                <span>Return to Dashboard</span>
              </button>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen flex flex-col pb-24 bg-[#F7FAF4]">
      {/* Dynamic Header */}
      <Header profile={mockFarmerProfile} weather={mockWeatherData} />

      {/* Main Grid Content */}
      <main className="mx-auto w-full max-w-lg md:max-w-5xl flex-1 px-4 py-6 md:px-6">
        {renderTabContent()}
      </main>

      {/* Bottom Sticky Navigation */}
      <BottomNavigation activeTab={activeTab} onChangeTab={setActiveTab} />
    </div>
  );
};
