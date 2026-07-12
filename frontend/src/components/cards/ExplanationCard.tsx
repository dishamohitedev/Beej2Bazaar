import React from 'react';
import { Sparkles } from 'lucide-react';

interface ExplanationCardProps {
  explanation: string;
}

export const ExplanationCard: React.FC<ExplanationCardProps> = ({ explanation }) => {
  return (
    <div className="rounded-[20px] border border-[#2e7d32]/15 bg-gradient-to-br from-emerald-500/5 to-transparent p-5">
      <div className="flex items-center gap-2 mb-3 text-[#2E7D32]">
        <Sparkles size={16} className="animate-pulse" />
        <span className="text-[10px] font-bold uppercase tracking-wider">
          Gemini AI Explanation
        </span>
      </div>
      <p className="text-xs font-semibold text-[#2E7D32]/90 leading-relaxed">
        {explanation}
      </p>
    </div>
  );
};
