import React from 'react';
import { Card } from '../ui/Card';
import { Sparkles, Activity } from 'lucide-react';
import { ConfidenceBadge } from './ConfidenceBadge';

interface PredictionCardProps {
  diseaseName: string;
  confidence: number;
  delay?: number;
}

export const PredictionCard: React.FC<PredictionCardProps> = ({
  diseaseName,
  confidence,
  delay = 0
}) => {
  return (
    <Card delay={delay} className="col-span-1 border border-slate-100/50 bg-gradient-to-br from-white to-[#F7FAF4] relative overflow-hidden">
      {/* Decorative pulse blur */}
      <div className="absolute top-[-20px] right-[-20px] w-36 h-36 bg-[#2E7D32]/10 rounded-full blur-3xl pointer-events-none" />

      <div className="flex justify-between items-start mb-6">
        <div>
          <h2 className="text-[10px] font-bold uppercase tracking-wider text-slate-400">AI Diagnosis</h2>
          <p className="text-sm font-bold text-[#2E7D32] mt-0.5">Detection Engine Results</p>
        </div>
        <div className="h-10 w-10 rounded-2xl bg-[#2E7D32]/10 flex items-center justify-center text-[#2E7D32]">
          <Activity size={20} className="animate-pulse" />
        </div>
      </div>

      <div className="space-y-4">
        <div>
          <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Identified Disease</span>
          <h3 className="text-xl font-extrabold text-slate-800 tracking-tight leading-snug mt-1">
            {diseaseName}
          </h3>
        </div>

        <div className="flex items-center gap-3 pt-2 border-t border-slate-100">
          <div className="flex-1 flex flex-col">
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1">Model Confidence</span>
            <div className="flex items-center gap-3">
              <ConfidenceBadge percentage={Math.round(confidence)} />
              <span className="text-xs text-slate-500 font-semibold">
                High Precision Match
              </span>
            </div>
          </div>
        </div>

        {/* Diagnostic confidence progress bar */}
        <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden mt-1.5">
          <div 
            className="h-full bg-gradient-to-r from-[#4CAF50] to-[#2E7D32] rounded-full transition-all duration-1000"
            style={{ width: `${confidence}%` }}
          />
        </div>
      </div>
    </Card>
  );
};
