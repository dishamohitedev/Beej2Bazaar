import React from 'react';

interface FactorCardProps {
  label: string;
  value: string;
  icon: React.ReactNode;
}

export const FactorCard: React.FC<FactorCardProps> = ({ label, value, icon }) => {
  return (
    <div className="flex items-center gap-3.5 p-4 rounded-2xl bg-slate-50 border border-slate-100/50 hover:bg-slate-100/40 transition-all duration-200">
      <div className="h-9 w-9 rounded-xl bg-white border border-slate-100 flex items-center justify-center text-[#2E7D32] shadow-sm shrink-0">
        {icon}
      </div>
      <div className="flex flex-col min-w-0">
        <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">{label}</span>
        <span className="text-sm font-extrabold text-slate-700 truncate mt-0.5">{value}</span>
      </div>
    </div>
  );
};
