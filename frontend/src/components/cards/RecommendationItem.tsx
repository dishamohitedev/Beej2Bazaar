import React from 'react';
import { CropRecommendationDetail } from '../../types';
import { ConfidenceBadge } from './ConfidenceBadge';

interface RecommendationItemProps {
  crop: CropRecommendationDetail;
  onSelect: () => void;
  isSelected: boolean;
}

export const RecommendationItem: React.FC<RecommendationItemProps> = ({ crop, onSelect, isSelected }) => {
  return (
    <div
      onClick={onSelect}
      className={`p-4 rounded-2xl border flex items-center justify-between transition-all duration-200 cursor-pointer ${
        isSelected
          ? 'bg-[#2E7D32]/5 border-[#2E7D32]/20 shadow-sm'
          : 'bg-white border-slate-100/70 hover:bg-slate-55 hover:border-slate-200'
      }`}
    >
      <div className="flex flex-col min-w-0">
        <h4 className="text-sm font-bold text-slate-850 truncate">{crop.cropName}</h4>
        <span className="text-[10px] text-slate-400 font-bold mt-0.5">
          Profit: <span className="text-slate-650 font-extrabold">₹{crop.expectedProfitPerAcre.toLocaleString()}/Acre</span>
        </span>
      </div>

      <div className="flex items-center gap-3">
        <ConfidenceBadge percentage={crop.matchPercentage} />
        <span className={`text-[10px] font-bold uppercase transition-colors ${
          isSelected ? 'text-[#2E7D32]' : 'text-slate-400'
        }`}>
          {isSelected ? 'Viewing' : 'Select'}
        </span>
      </div>
    </div>
  );
};
