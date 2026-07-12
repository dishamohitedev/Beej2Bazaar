import React from 'react';
import { Card } from '../ui/Card';
import { CropSuggestion } from '../../types';
import { Sparkles, TrendingUp, TrendingDown, Minus } from 'lucide-react';

interface RecommendationCardProps {
  suggestions: CropSuggestion[];
  delay?: number;
}

export const RecommendationCard: React.FC<RecommendationCardProps> = ({ suggestions, delay = 0 }) => {
  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'up':
        return <TrendingUp size={14} className="text-[#2E7D32]" />;
      case 'down':
        return <TrendingDown size={14} className="text-red-500" />;
      default:
        return <Minus size={14} className="text-slate-400" />;
    }
  };

  return (
    <Card delay={delay} className="flex flex-col justify-between">
      <div>
        <div className="flex justify-between items-start mb-4">
          <h2 className="text-[10px] font-bold uppercase tracking-wider text-slate-400">AI Recommendations</h2>
          <div className="h-7 w-7 rounded-lg bg-emerald-50 flex items-center justify-center text-[#2E7D32]">
            <Sparkles size={15} />
          </div>
        </div>

        <p className="text-xs text-slate-500 font-semibold mb-4 leading-relaxed">
          Top crops suggested for your soil type and upcoming monsoon:
        </p>

        <div className="space-y-3.5">
          {suggestions.map((item) => (
            <div key={item.id} className="p-3 bg-slate-50 border border-slate-100 rounded-2xl flex flex-col gap-1.5 hover:bg-slate-100/50 transition-all duration-200">
              <div className="flex justify-between items-center">
                <span className="text-xs font-bold text-slate-800">{item.cropName}</span>
                <span className="text-[10px] font-black text-[#2E7D32] bg-[#2E7D32]/10 px-2 py-0.5 rounded-full">
                  {item.matchPercentage}% match
                </span>
              </div>

              {/* Progress bar match */}
              <div className="h-1.5 w-full bg-slate-200 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-[#2E7D32]"
                  style={{ width: `${item.matchPercentage}%` }}
                />
              </div>

              <div className="flex justify-between items-center mt-1 text-[10px] text-slate-400 font-bold">
                <span>Revenue: <span className="text-slate-650">{item.expectedRevenue}</span></span>
                <div className="flex items-center gap-1">
                  <span>Trend:</span>
                  {getTrendIcon(item.marketTrend)}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="mt-5 pt-3 border-t border-slate-100 text-center">
        <button className="text-xs font-bold text-[#2E7D32] hover:text-[#4CAF50] cursor-pointer">
          Run Advanced Analysis →
        </button>
      </div>
    </Card>
  );
};
