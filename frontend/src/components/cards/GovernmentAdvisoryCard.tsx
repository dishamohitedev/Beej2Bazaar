import React from 'react';
import { Card } from '../ui/Card';
import { Landmark, AlertTriangle } from 'lucide-react';

interface GovernmentAdvisoryCardProps {
  advisory: string;
  delay?: number;
}

export const GovernmentAdvisoryCard: React.FC<GovernmentAdvisoryCardProps> = ({
  advisory,
  delay = 0
}) => {
  return (
    <Card delay={delay} className="border border-amber-100 bg-gradient-to-br from-white to-amber-50/15 relative overflow-hidden">
      {/* Decorative official badge/seal look */}
      <div className="absolute top-[-30px] right-[-30px] w-36 h-36 bg-[#F9A826]/5 rounded-full blur-2xl pointer-events-none" />

      <div className="flex justify-between items-start mb-4">
        <div>
          <h2 className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Department Advisory</h2>
          <p className="text-sm font-bold text-amber-700 mt-0.5">Official Government Circular</p>
        </div>
        <div className="h-10 w-10 rounded-2xl bg-amber-50 text-amber-600 flex items-center justify-center">
          <Landmark size={18} />
        </div>
      </div>

      <div className="space-y-3.5">
        {/* Notice heading */}
        <div className="flex items-center gap-2 text-[10px] text-amber-750 font-extrabold uppercase tracking-wide bg-amber-500/5 p-2 rounded-lg border border-amber-500/10">
          <AlertTriangle size={12} className="stroke-[2.5px] text-amber-600" />
          <span>Active Agricultural Alert</span>
        </div>

        {/* Advisory text body */}
        <p className="text-xs font-semibold text-slate-650 leading-relaxed bg-white p-3 rounded-xl border border-slate-100/70 shadow-sm">
          {advisory}
        </p>

        {/* Official seal footer */}
        <div className="flex justify-between items-center text-[9px] font-bold text-slate-400 uppercase tracking-widest mt-1 border-t border-slate-100 pt-3">
          <span>Kharif Crop Protection Desk</span>
          <span>Krishi Vigyan Kendra</span>
        </div>
      </div>
    </Card>
  );
};
