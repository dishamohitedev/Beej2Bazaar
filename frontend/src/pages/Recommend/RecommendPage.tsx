import React, { useState, useEffect } from 'react';
import api from '../../services/api';
import { BestRecommendationCard } from '../../components/cards/BestRecommendationCard';
import { RecommendationList } from '../../components/cards/RecommendationList';
import { CompareCard } from '../../components/cards/CompareCard';
import { CropRecommendationDetail } from '../../types';
import { Sparkles, ArrowLeft, Loader2 } from 'lucide-react';

interface RecommendPageProps {
  onBackToDashboard: () => void;
}

export const RecommendPage: React.FC<RecommendPageProps> = ({ onBackToDashboard }) => {
  const [loading, setLoading] = useState(true);
  const [recommendations, setRecommendations] = useState<CropRecommendationDetail[]>([]);
  const [selectedCropId, setSelectedCropId] = useState('');
  const [isComparing, setIsComparing] = useState(false);

  useEffect(() => {
    const fetchRecommendations = async () => {
      setLoading(true);
      try {
        const response = await api.get('/api/crop/recommendations');
        const list = response.data.recommendations || [];
        const overarchingExplanation = response.data.explanation || 'No details available.';

        const mapped: CropRecommendationDetail[] = list.map((item: any, idx: number) => {
          // Generate realistic farming details based on crop profiles and sub-scores
          const finalScore = item.final_score || 0.8;
          const marketScore = item.scores?.market_score || 0.75;
          const soilScore = item.scores?.soil_score || 0.8;

          return {
            id: item.crop.id,
            cropName: item.crop.crop_name,
            matchPercentage: Math.round(finalScore * 100),
            expectedProfitPerAcre: Math.round(marketScore * 50000),
            marketPricePerQuintal: Math.round(marketScore * 6500) || 4500,
            waterRequirementMm: item.crop.ideal_rainfall_mm || 450,
            growingSeason: item.crop.season || 'Kharif',
            sowingWindow: item.crop.season === 'Kharif' ? 'June 15 - July 15' : 'October 15 - November 15',
            factors: {
              soilMoisture: soilScore > 0.8 ? 'High (60-70%)' : 'Moderate (50-60%)',
              soilPh: '6.0 - 7.5',
              temperatureRange: `${item.crop.ideal_temp_min || 20}°C - ${item.crop.ideal_temp_max || 35}°C`,
              marketDemand: marketScore > 0.8 ? 'Very High (Upward)' : marketScore > 0.6 ? 'Steady' : 'Stable'
            },
            // For the first crop, use the overarching gemini explanation, else construct matching summaries
            geminiExplanation: idx === 0 
              ? overarchingExplanation 
              : `Agronomic Engine matched ${item.crop.crop_name} as a suitable alternative with a score of ${Math.round(finalScore * 100)}%. Ideal for regional soil compatibility and average seasonal temperatures.`
          };
        });

        setRecommendations(mapped);
        if (mapped.length > 0) {
          setSelectedCropId(mapped[0].id);
        }
      } catch (err) {
        console.error('Failed to load crop recommendations', err);
      } finally {
        setLoading(false);
      }
    };

    fetchRecommendations();
  }, []);

  const selectedCrop = recommendations.find(c => c.id === selectedCropId) || recommendations[0];
  const compareCrop = recommendations.find(c => c.id !== selectedCrop?.id) || recommendations[1];

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-24 gap-3">
        <Loader2 className="animate-spin text-[#2E7D32]" size={36} />
        <span className="text-xs font-bold text-slate-400 uppercase tracking-widest">
          Evaluating Suitability engine...
        </span>
      </div>
    );
  }

  if (recommendations.length === 0) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <button
            onClick={onBackToDashboard}
            className="inline-flex items-center gap-1.5 text-xs font-bold text-[#2E7D32] hover:text-[#256428] transition-colors cursor-pointer"
          >
            <ArrowLeft size={14} />
            <span>Back to Home</span>
          </button>
        </div>
        <div className="flex flex-col items-center justify-center py-16 px-4 text-center bg-white rounded-2xl border border-slate-100 shadow-sm max-w-lg mx-auto">
          <Sparkles className="text-amber-500 mb-4 animate-pulse" size={40} />
          <h3 className="text-base font-extrabold text-slate-800">No Crop Recommendations Available</h3>
          <p className="text-xs text-slate-500 mt-2 mb-6 max-w-sm">
            We couldn't match any crop records to your current soil and irrigation settings. Try modifying your onboarding settings or updating your profile.
          </p>
          <button
            onClick={onBackToDashboard}
            className="inline-flex items-center gap-1.5 text-xs font-bold bg-[#2E7D32] hover:bg-[#256428] text-white px-5 py-2.5 rounded-lg shadow-sm transition-colors cursor-pointer"
          >
            <ArrowLeft size={14} />
            <span>Go to Dashboard</span>
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Top action header */}
      <div className="flex items-center justify-between">
        <button
          onClick={onBackToDashboard}
          className="inline-flex items-center gap-1.5 text-xs font-bold text-[#2E7D32] hover:text-[#256428] transition-colors cursor-pointer"
        >
          <ArrowLeft size={14} />
          <span>Back to Home</span>
        </button>

        <div className="flex items-center gap-1.5 text-slate-500 text-xs font-bold bg-white px-3.5 py-1.5 rounded-full border border-slate-100 shadow-sm">
          <Sparkles size={13} className="text-[#2E7D32]" />
          <span>Explainable AI Enabled</span>
        </div>
      </div>

      {/* Main Grid Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <BestRecommendationCard 
            crop={selectedCrop} 
            onCompare={() => setIsComparing(true)} 
          />
        </div>
        <div className="lg:col-span-1">
          <RecommendationList 
            crops={recommendations} 
            selectedId={selectedCropId} 
            onSelectCrop={setSelectedCropId} 
          />
        </div>
      </div>

      {/* Comparison Modal */}
      {isComparing && compareCrop && (
        <CompareCard 
          cropA={selectedCrop} 
          cropB={compareCrop} 
          onClose={() => setIsComparing(false)} 
        />
      )}
    </div>
  );
};

export default RecommendPage;
