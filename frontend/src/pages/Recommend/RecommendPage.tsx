import React, { useState } from 'react';
import { BestRecommendationCard } from '../../components/cards/BestRecommendationCard';
import { RecommendationList } from '../../components/cards/RecommendationList';
import { CompareCard } from '../../components/cards/CompareCard';
import { CropRecommendationDetail } from '../../types';
import { Sparkles, ArrowLeft } from 'lucide-react';

interface RecommendPageProps {
  onBackToDashboard: () => void;
}

const mockRecommendations: CropRecommendationDetail[] = [
  {
    id: 'crop-1',
    cropName: 'Soybean (JS 335)',
    matchPercentage: 96,
    expectedProfitPerAcre: 48000,
    marketPricePerQuintal: 4650,
    waterRequirementMm: 450,
    growingSeason: 'Kharif',
    sowingWindow: 'June 15 - July 10',
    factors: {
      soilMoisture: 'High (60-70%)',
      soilPh: '6.0 - 7.5',
      temperatureRange: '20°C - 35°C',
      marketDemand: 'Very High (Upward)'
    },
    geminiExplanation: 'Agronomic Decision Engine selected Soybean as the optimal choice because the forecasted monsoon onset matches the seedling phase. Soil nitrogen status is highly compatible, and current Nashik Mandi buyer quotes indicate a strong upward demand curve for oilseed processing units.'
  },
  {
    id: 'crop-2',
    cropName: 'Bt Cotton (Kharif)',
    matchPercentage: 88,
    expectedProfitPerAcre: 42000,
    marketPricePerQuintal: 7200,
    waterRequirementMm: 650,
    growingSeason: 'Kharif',
    sowingWindow: 'June 1 - June 20',
    factors: {
      soilMoisture: 'Moderate (50-60%)',
      soilPh: '5.8 - 8.0',
      temperatureRange: '22°C - 38°C',
      marketDemand: 'Steady (Stable)'
    },
    geminiExplanation: 'Cotton shows a high suitability match due to excellent deep black soil water drainage. Sowing within the June window avoids late-stage pest vulnerabilities. Local buyer demand remains steady, though water demand is moderately higher than Soybean.'
  },
  {
    id: 'crop-3',
    cropName: 'Pigeon Pea (Tur)',
    matchPercentage: 84,
    expectedProfitPerAcre: 38000,
    marketPricePerQuintal: 8400,
    waterRequirementMm: 350,
    growingSeason: 'Kharif',
    sowingWindow: 'June 15 - July 15',
    factors: {
      soilMoisture: 'Low (40-50%)',
      soilPh: '6.5 - 7.8',
      temperatureRange: '18°C - 32°C',
      marketDemand: 'High (Stable)'
    },
    geminiExplanation: 'Pigeon Pea is recommended due to its high drought tolerance and low irrigation needs. Recommended to plant in rotation to restore soil nitrogen. Expected APMC rates are stable with minimal price volatility predicted.'
  },
  {
    id: 'crop-4',
    cropName: 'Maize (Pioneer)',
    matchPercentage: 78,
    expectedProfitPerAcre: 31000,
    marketPricePerQuintal: 2150,
    waterRequirementMm: 500,
    growingSeason: 'Kharif',
    sowingWindow: 'June 20 - July 15',
    factors: {
      soilMoisture: 'Moderate (55-65%)',
      soilPh: '5.5 - 7.5',
      temperatureRange: '15°C - 35°C',
      marketDemand: 'Moderate (Stable)'
    },
    geminiExplanation: 'Maize is a reliable alternative with high yield indices. Recommended for well-drained loamy soil sections. Highly compatible with quick nutrient spray regimes and standard nitrogen applications.'
  },
  {
    id: 'crop-5',
    cropName: 'Moong (Green Gram)',
    matchPercentage: 75,
    expectedProfitPerAcre: 26000,
    marketPricePerQuintal: 7800,
    waterRequirementMm: 300,
    growingSeason: 'Kharif',
    sowingWindow: 'June 25 - July 10',
    factors: {
      soilMoisture: 'Low (35-45%)',
      soilPh: '6.2 - 7.2',
      temperatureRange: '20°C - 35°C',
      marketDemand: 'Moderate (Stable)'
    },
    geminiExplanation: 'A short-duration crop (60-70 days) that requires minimal water and matures rapidly. Ideal for double-cropping systems. Provides rapid post-harvest soil enrichment.'
  }
];

export const RecommendPage: React.FC<RecommendPageProps> = ({ onBackToDashboard }) => {
  const [selectedCropId, setSelectedCropId] = useState(mockRecommendations[0].id);
  const [isComparing, setIsComparing] = useState(false);

  const selectedCrop = mockRecommendations.find(c => c.id === selectedCropId) || mockRecommendations[0];
  // Compare selected crop with the next crop in list by default
  const compareCrop = mockRecommendations.find(c => c.id !== selectedCrop.id) || mockRecommendations[1];

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
            crops={mockRecommendations} 
            selectedId={selectedCropId} 
            onSelectCrop={setSelectedCropId} 
          />
        </div>
      </div>

      {/* Comparison Modal */}
      {isComparing && (
        <CompareCard 
          cropA={selectedCrop} 
          cropB={compareCrop} 
          onClose={() => setIsComparing(false)} 
        />
      )}
    </div>
  );
};
