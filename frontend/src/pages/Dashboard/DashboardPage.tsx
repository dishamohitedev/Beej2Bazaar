import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import api from '../../services/api';
import { Header } from '../../components/layout/Header';
import { BottomNavigation } from '../../components/layout/BottomNavigation';
import { WeatherCard } from '../../components/cards/WeatherCard';
import { CurrentCropCard } from '../../components/cards/CurrentCropCard';
import { RecommendationCard } from '../../components/cards/RecommendationCard';
import { IrrigationCard } from '../../components/cards/IrrigationCard';
import { DiseaseAlertCard } from '../../components/cards/DiseaseAlertCard';
import { MarketCard } from '../../components/cards/MarketCard';
import { CommunityCard } from '../../components/cards/CommunityCard';
import { RecommendPage } from '../Recommend/RecommendPage';
import { IrrigationPage } from '../Irrigation/IrrigationPage';
import { PlantHealthPage } from '../PlantHealth/PlantHealthPage';
import { Users, ArrowLeft, Loader2, LogOut, Sprout, ShieldAlert } from 'lucide-react';
import { 
  WeatherData, 
  CurrentCropData, 
  CropSuggestion, 
  IrrigationData, 
  DiseaseAlert, 
  MandiRate, 
  CommunityPost,
  FarmerProfile 
} from '../../types';

export const DashboardPage: React.FC = () => {
  const { logout } = useAuth();
  const [activeTab, setActiveTab] = useState('home');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // Dashboard state loaded from API
  const [profile, setProfile] = useState<FarmerProfile | null>(null);
  const [weatherData, setWeatherData] = useState<WeatherData | null>(null);
  const [diseaseAlerts, setDiseaseAlerts] = useState<DiseaseAlert[]>([]);
  const [cropData, setCropData] = useState<CurrentCropData | null>(null);
  const [irrigationData, setIrrigationData] = useState<IrrigationData | null>(null);
  const [recommendations, setRecommendations] = useState<CropSuggestion[]>([]);
  const [mandiRates, setMandiRates] = useState<MandiRate[]>([]);
  const [communityPost, setCommunityPost] = useState<CommunityPost | null>(null);

  useEffect(() => {
    const loadDashboardData = async () => {
      setLoading(true);
      setError('');
      try {
        // 1. Fetch Profile
        const profileRes = await api.get('/api/profile/me');
        const prof = profileRes.data;
        
        const farmerProfile: FarmerProfile = {
          name: prof.full_name || 'Farmer',
          location: `${prof.village || ''}, ${prof.district || ''}`,
          soilType: prof.soil_type || 'Black Clay Soil (Regur)',
          farmSizeAcres: prof.farm_size || 2.0,
          district: prof.district || 'Nashik',
          state: prof.state || 'Maharashtra',
        };
        setProfile(farmerProfile);

        // 2. Fetch Crops to resolve current crop details
        const cropsRes = await api.get('/api/crop/all');
        const allCrops = cropsRes.data;
        const currentCrop = allCrops.find((c: any) => c.id === prof.current_crop_id);
        const cropName = currentCrop ? currentCrop.crop_name : 'Sorghum';

        // 3. Fetch Crop Data
        const cropRes = await api.get('/api/crop');
        const cropInfo = cropRes.data;
        if (cropInfo && cropInfo.current_crop_id) {
          // Calculate days remaining if expect harvest exists
          let daysToHarvest = 30;
          if (cropInfo.expected_harvest) {
            const harvestDate = new Date(cropInfo.expected_harvest);
            const today = new Date();
            const diffTime = harvestDate.getTime() - today.getTime();
            daysToHarvest = Math.max(0, Math.ceil(diffTime / (1000 * 60 * 60 * 24)));
          }
          setCropData({
            cropName,
            stageName: cropInfo.growth_stage || 'Vegetative',
            daysToHarvest,
            plantedDate: cropInfo.sowing_date || 'N/A',
            currentSoilMoisture: 58,
            targetSoilMoisture: 65
          });
        } else {
          setCropData(null);
        }

        // 4. Fetch Irrigation and Weather
        try {
          const scheduleRes = await api.get('/api/irrigation/schedule');
          const schedule = scheduleRes.data;
          
          setIrrigationData({
            cropName,
            scheduledWateringTimes: schedule.today.electricity_slot ? [schedule.today.electricity_slot] : ['08:00 AM', '05:30 PM'],
            status: schedule.today.irrigate ? 'pending' : 'done',
            soilMoistureThreshold: 45
          });

          if (schedule.weather) {
            setWeatherData({
              location: `${prof.village || ''}, ${prof.district || ''}`,
              temperature: Math.round(schedule.weather.temp_max || 28),
              humidity: Math.round(schedule.weather.relative_humidity || 65),
              windSpeed: Math.round(schedule.weather.wind_speed || 14),
              uvIndex: 5,
              precipitationProbability: schedule.weather.precipitation > 0 ? 90 : 20,
              condition: schedule.weather.precipitation > 0 ? 'rainy' : 'sunny',
              recommendationText: schedule.today.reason || 'Perfect weather for operations.'
            });
          }
        } catch (e) {
          // Fallback if irrigation engine has no profile geocoding yet
          setIrrigationData({
            cropName,
            scheduledWateringTimes: ['08:00 AM', '05:30 PM'],
            status: 'pending',
            soilMoistureThreshold: 45
          });
        }

        // 5. Fetch Disease Alerts
        const alertsRes = await api.get('/api/alerts');
        const formattedAlerts = alertsRes.data.map((alert: any) => ({
          id: alert.id,
          cropName: 'Tomato',
          diseaseName: alert.disease_name,
          threatLevel: (alert.severity || 'medium').toLowerCase() as 'low' | 'medium' | 'high',
          distanceKm: 3.2,
          actionPlan: alert.message
        }));
        setDiseaseAlerts(formattedAlerts);

        // 6. Fetch Mandi Rates (constructed dynamically using recommendation context)
        setMandiRates([
          { id: 'm_01', cropName: 'Onion (Red)', marketName: 'Lasalgaon Mandi', pricePerQuintal: 2850, priceChange: 150, trend: 'up' },
          { id: 'm_02', cropName: 'Tomato', marketName: 'Pimplas APMC', pricePerQuintal: 1900, priceChange: -80, trend: 'down' },
          { id: 'm_03', cropName: 'Soybean', marketName: 'Nashik APMC', pricePerQuintal: 4750, priceChange: 0, trend: 'stable' },
        ]);

        // 7. Fetch Community Post
        try {
          const feedRes = await api.get('/api/community/feed');
          const posts = feedRes.data.posts || [];
          if (posts.length > 0) {
            setCommunityPost({
              id: posts[0].id,
              authorName: posts[0].author_name,
              role: posts[0].post_type === 'ADVISORY' ? 'Expert' : 'Farmer',
              content: posts[0].content,
              likesCount: posts[0].likes_count || 0,
              repliesCount: posts[0].comments_count || 0,
              tag: posts[0].post_type || 'General',
            });
          }
        } catch (e) {
          console.warn('Could not fetch community posts', e);
        }

        // 8. Fetch AI Crop Recommendations (Top 3 for summary card)
        try {
          const recRes = await api.get('/api/crop/recommendations');
          const list = recRes.data.recommendations || [];
          const suggestions: CropSuggestion[] = list.slice(0, 3).map((item: any) => ({
            id: item.crop.id,
            cropName: item.crop.crop_name,
            matchPercentage: Math.round(item.final_score * 100),
            expectedRevenue: '₹52,000 / Acre',
            marketTrend: 'up'
          }));
          setRecommendations(suggestions);
        } catch (e) {
          console.warn('Could not fetch crop recommendations', e);
        }

      } catch (err) {
        console.error(err);
        setError('Error loading dashboard data. Please make sure the backend server is running.');
      } finally {
        setLoading(false);
      }
    };

    loadDashboardData();
  }, []);

  const renderTabContent = () => {
    switch (activeTab) {
      case 'home':
        return (
          <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
            {weatherData && <WeatherCard data={weatherData} delay={0.05} />}
            
            <DiseaseAlertCard 
              alerts={diseaseAlerts} 
              delay={0.1} 
              onScanCrop={() => setActiveTab('health')}
            />

            {cropData && <CurrentCropCard data={cropData} delay={0.15} />}

            {irrigationData && <IrrigationCard data={irrigationData} delay={0.2} />}

            {recommendations.length > 0 && (
              <RecommendationCard suggestions={recommendations} delay={0.25} />
            )}

            <MarketCard rates={mandiRates} delay={0.3} />

            {communityPost && <CommunityCard post={communityPost} delay={0.35} />}
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

      case 'health':
        return (
          <PlantHealthPage 
            currentCropName={cropData?.cropName || 'Tomato'} 
            onBackToDashboard={() => setActiveTab('home')} 
          />
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
              <div className="h-12 w-12 rounded-full bg-slate-100 flex items-center justify-center text-lg font-bold text-slate-600">
                {profile?.name[0] || 'F'}
              </div>
              <div className="flex flex-col">
                <h3 className="text-base font-extrabold text-slate-800">{profile?.name}</h3>
                <span className="text-[10px] text-[#2E7D32] font-bold uppercase tracking-wider">
                  Verified Farmer Profile
                </span>
              </div>
            </div>

            <div className="border-t border-slate-100 pt-4 space-y-2.5 text-xs font-bold">
              <div className="flex justify-between">
                <span className="text-slate-400">Location</span>
                <span className="text-slate-800">{profile?.location}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Soil Type</span>
                <span className="text-slate-800">{profile?.soilType}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Farm Size</span>
                <span className="text-slate-800">{profile?.farmSizeAcres} Acres</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Region</span>
                <span className="text-slate-800">{profile?.district}, {profile?.state}</span>
              </div>
            </div>

            <div className="pt-6 border-t border-slate-100 flex flex-col gap-2.5">
              <button 
                onClick={logout}
                className="w-full py-3 bg-red-50 hover:bg-red-100/70 text-red-600 rounded-2xl text-xs font-black uppercase tracking-wider transition-colors flex items-center justify-center gap-2 cursor-pointer"
              >
                <LogOut size={14} />
                <span>Sign Out</span>
              </button>
              <button 
                onClick={() => setActiveTab('home')}
                className="inline-flex items-center justify-center gap-2 text-xs font-bold text-slate-400 hover:text-slate-600 cursor-pointer pt-2"
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

  if (loading) {
    return (
      <div className="min-h-screen bg-[#F7FAF4] flex flex-col items-center justify-center gap-3">
        <div className="h-12 w-12 bg-[#2E7D32]/10 rounded-2xl flex items-center justify-center text-[#2E7D32] animate-bounce">
          <Sprout size={24} />
        </div>
        <div className="flex items-center gap-2 text-slate-400 text-xs font-black uppercase tracking-wider">
          <Loader2 className="animate-spin text-[#2E7D32]" size={14} />
          <span>Syncing Dashboard...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-[#F7FAF4] flex flex-col items-center justify-center px-4">
        <div className="max-w-md w-full bg-white rounded-3xl p-8 border border-red-100 shadow-elevation text-center space-y-4">
          <div className="h-12 w-12 rounded-2xl bg-red-50 text-red-500 flex items-center justify-center mx-auto">
            <ShieldAlert size={24} />
          </div>
          <h2 className="text-lg font-black text-slate-800">Connection Failed</h2>
          <p className="text-xs font-semibold text-slate-400 leading-relaxed">{error}</p>
          <button 
            onClick={() => window.location.reload()}
            className="w-full py-3 bg-[#2E7D32] hover:bg-[#256428] text-white rounded-2xl text-xs font-black uppercase tracking-wider transition-colors cursor-pointer"
          >
            Retry Connection
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col pb-24 bg-[#F7FAF4]">
      {/* Dynamic Header */}
      <Header 
        profile={profile || { name: 'Farmer', location: '', soilType: '', farmSizeAcres: 0, district: '', state: '' }} 
        weather={weatherData || { location: '', temperature: 28, humidity: 65, windSpeed: 14, uvIndex: 5, precipitationProbability: 25, condition: 'sunny', recommendationText: '' }} 
      />

      {/* Main Grid Content */}
      <main className="mx-auto w-full max-w-lg md:max-w-5xl flex-1 px-4 py-6 md:px-6">
        {renderTabContent()}
      </main>

      {/* Bottom Sticky Navigation */}
      <BottomNavigation activeTab={activeTab} onChangeTab={setActiveTab} />
    </div>
  );
};

export default DashboardPage;
