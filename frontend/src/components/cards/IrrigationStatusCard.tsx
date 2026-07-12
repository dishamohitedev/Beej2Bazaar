import React from 'react';
import { IrrigationToday } from '../../types';
import { CheckCircle2, XCircle, Droplets, CalendarClock, AlertCircle } from 'lucide-react';

interface IrrigationStatusCardProps {
  today: IrrigationToday;
  next_irrigation: string;
}

export const IrrigationStatusCard: React.FC<IrrigationStatusCardProps> = ({ today, next_irrigation }) => {
  return (
    <div className={`relative overflow-hidden rounded-[24px] p-6 border shadow-[0_8px_32px_rgba(0,0,0,0.06)] transition-all ${
      today.irrigate
        ? 'bg-gradient-to-br from-[#2E7D32]/8 to-[#4CAF50]/4 border-[#2E7D32]/20'
        : 'bg-gradient-to-br from-slate-50 to-white border-slate-100'
    }`}>
      {/* Background glow */}
      <div className={`absolute right-[-40px] top-[-40px] h-48 w-48 rounded-full blur-3xl pointer-events-none ${
        today.irrigate ? 'bg-[#4CAF50]/10' : 'bg-slate-200/40'
      }`} />

      {/* Section label */}
      <p className="text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-4">Today's Irrigation Status</p>

      {/* Main status */}
      <div className="flex items-center gap-4 mb-6">
        {today.irrigate ? (
          <div className="h-14 w-14 rounded-2xl bg-[#2E7D32]/10 border border-[#2E7D32]/15 flex items-center justify-center shrink-0">
            <CheckCircle2 size={28} className="text-[#2E7D32]" />
          </div>
        ) : (
          <div className="h-14 w-14 rounded-2xl bg-slate-100 border border-slate-200 flex items-center justify-center shrink-0">
            <XCircle size={28} className="text-slate-400" />
          </div>
        )}
        <div>
          <h2 className={`text-2xl font-black tracking-tight ${today.irrigate ? 'text-[#2E7D32]' : 'text-slate-600'}`}>
            {today.irrigate ? 'Irrigate Today' : 'No Irrigation Needed'}
          </h2>
          <p className="text-xs font-semibold text-slate-500 mt-0.5">WME Recommendation</p>
        </div>
      </div>

      {/* Metrics row */}
      <div className="grid grid-cols-2 gap-3 mb-5">
        <div className="flex items-center gap-3 bg-white/80 rounded-2xl p-3.5 border border-slate-100">
          <Droplets size={18} className="text-blue-500 shrink-0" />
          <div>
            <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Water Required</p>
            <p className="text-base font-black text-slate-800">{today.water_mm} mm</p>
          </div>
        </div>
        <div className="flex items-center gap-3 bg-white/80 rounded-2xl p-3.5 border border-slate-100">
          <CalendarClock size={18} className="text-[#2E7D32] shrink-0" />
          <div>
            <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Next Irrigation</p>
            <p className="text-base font-black text-slate-800">{next_irrigation}</p>
          </div>
        </div>
      </div>

      {/* Reason banner */}
      <div className="flex items-start gap-2.5 bg-white/70 rounded-2xl p-3.5 border border-slate-100/80">
        <AlertCircle size={15} className="text-[#F9A826] mt-0.5 shrink-0" />
        <div>
          <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-0.5">Reason</p>
          <p className="text-xs font-semibold text-slate-700 leading-relaxed">{today.reason}</p>
        </div>
      </div>
    </div>
  );
};
