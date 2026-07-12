import React from 'react';

interface ConfidenceBadgeProps {
  percentage: number;
}

export const ConfidenceBadge: React.FC<ConfidenceBadgeProps> = ({ percentage }) => {
  const getColors = () => {
    if (percentage >= 90) return 'bg-[#2E7D32]/10 text-[#2E7D32] border-[#2E7D32]/25';
    if (percentage >= 75) return 'bg-[#F9A826]/10 text-[#D97706] border-[#F9A826]/25';
    return 'bg-slate-100 text-slate-600 border-slate-200';
  };

  return (
    <span className={`inline-flex items-center gap-1.5 rounded-full border px-3 py-1 text-[10px] font-bold uppercase tracking-wider ${getColors()}`}>
      <span className="h-1.5 w-1.5 rounded-full bg-current animate-pulse" />
      {percentage}% Match
    </span>
  );
};
