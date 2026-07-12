import React from 'react';
import { Card } from '../ui/Card';
import { CropRecommendationDetail } from '../../types';
import { RecommendationItem } from './RecommendationItem';
import { BarChart3 } from 'lucide-react';

interface RecommendationListProps {
  crops: CropRecommendationDetail[];
  selectedId: string;
  onSelectCrop: (id: string) => void;
}

export const RecommendationList: React.FC<RecommendationListProps> = ({ crops, selectedId, onSelectCrop }) => {
  return (
    <Card className="flex flex-col gap-4">
      <div className="flex justify-between items-center pb-2 border-b border-slate-100">
        <div>
          <h2 className="text-[10px] font-bold uppercase tracking-wider text-slate-400">All Suggestions</h2>
          <h3 className="text-lg font-black text-slate-800 tracking-tight mt-0.5">Top Recommended Crops</h3>
        </div>
        <BarChart3 size={18} className="text-slate-400" />
      </div>

      <div className="space-y-3">
        {crops.map((crop) => (
          <RecommendationItem 
            key={crop.id} 
            crop={crop} 
            isSelected={crop.id === selectedId}
            onSelect={() => onSelectCrop(crop.id)}
          />
        ))}
      </div>
    </Card>
  );
};
