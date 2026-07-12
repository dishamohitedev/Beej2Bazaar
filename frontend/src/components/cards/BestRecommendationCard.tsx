import React from 'react';
import { Card } from '../ui/Card';
import { CropRecommendationDetail } from '../../types';
import { ConfidenceBadge } from './ConfidenceBadge';
import { FactorCard } from './FactorCard';
import { ExplanationCard } from './ExplanationCard';
import { DollarSign, Droplet, Calendar, BarChart3, Scale } from 'lucide-react';

interface BestRecommendationCardProps {
  crop: CropRecommendationDetail;
  onCompare: () => void;
}

export const BestRecommendationCard: React.FC<BestRecommendationCardProps> = ({ crop, onCompare }) => {
  return (
    <Card className="relative overflow-hidden bg-gradient-to-br from-white to-[#F7FAF4]/50 border-none shadow-soft-md">
      {/* Accent decoration */}
      <div className="absolute right-[-30px] top-[-30px] h-36 w-36 rounded-full bg-[#2E7D32]/5 blur-2xl pointer-events-none" />

      <div className="flex flex-wrap justify-between items-center gap-3 mb-6">
        <div>
          <span className="text-[10px] font-bold text-[#2E7D32] uppercase tracking-wider">
            ADE Top Recommendation
          </span>
          <h3 className="text-3xl font-black text-slate-900 tracking-tight mt-0.5">{crop.cropName}</h3>
        </div>
        <ConfidenceBadge percentage={crop.matchPercentage} />
      </div>

      {/* Sowing window pill */}
      <div className="mb-6 p-3 bg-white border border-slate-100/50 rounded-2xl flex items-center justify-between">
        <span className="text-xs text-slate-500 font-bold">Ideal Sowing Window</span>
        <span className="text-xs font-extrabold text-slate-700 bg-slate-100 px-3 py-1 rounded-full">
          {crop.sowingWindow}
        </span>
      </div>

      {/* Grid of Key Viability metrics */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-6">
        <FactorCard 
          label="Expected Profit" 
          value={`₹${crop.expectedProfitPerAcre.toLocaleString()}/Acre`} 
          icon={<DollarSign size={18} />} 
        />
        <FactorCard 
          label="Mandi Price" 
          value={`₹${crop.marketPricePerQuintal.toLocaleString()}/q`} 
          icon={<BarChart3 size={18} />} 
        />
        <FactorCard 
          label="Water Demand" 
          value={`${crop.waterRequirementMm} mm`} 
          icon={<Droplet size={18} />} 
        />
        <FactorCard 
          label="Growing Season" 
          value={crop.growingSeason} 
          icon={<Calendar size={18} />} 
        />
      </div>

      {/* Gemini AI explanation details */}
      <div className="mb-6">
        <ExplanationCard explanation={crop.geminiExplanation} />
      </div>

      {/* Compare button action */}
      <div className="border-t border-slate-100 pt-5">
        <button
          onClick={onCompare}
          className="w-full flex items-center justify-center gap-2 rounded-2xl bg-[#2E7D32] hover:bg-[#256428] py-3.5 px-4 text-xs font-bold text-white shadow-sm transition-all duration-200 cursor-pointer"
        >
          <Scale size={15} />
          <span>Compare with Other Crops</span>
        </button>
      </div>
    </Card>
  );
};
