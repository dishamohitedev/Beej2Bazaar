import React from 'react';
import { IrrigationDaySchedule } from '../../types';
import { Droplets, CloudRain, Sun, CheckCircle2 } from 'lucide-react';

interface ScheduleCardProps {
  day: IrrigationDaySchedule;
  isToday?: boolean;
}

export const ScheduleCard: React.FC<ScheduleCardProps> = ({ day, isToday }) => {
  const statusColors = {
    completed: 'text-[#2E7D32] bg-[#2E7D32]/8 border-[#2E7D32]/15',
    pending: day.irrigate ? 'text-blue-600 bg-blue-50 border-blue-100' : 'text-slate-500 bg-slate-50 border-slate-100',
    skipped: 'text-slate-400 bg-slate-50 border-slate-100',
  };

  return (
    <div className={`rounded-[20px] p-4 border flex flex-col gap-3 transition-all duration-200 ${
      isToday
        ? 'bg-gradient-to-b from-[#2E7D32]/6 to-white border-[#2E7D32]/20 shadow-[0_4px_16px_rgba(46,125,50,0.10)]'
        : 'bg-white border-slate-100 hover:border-slate-200 hover:shadow-sm'
    }`}>
      {/* Day header */}
      <div className="flex items-center justify-between">
        <div>
          <p className={`text-[10px] font-extrabold uppercase tracking-wider ${isToday ? 'text-[#2E7D32]' : 'text-slate-400'}`}>
            {isToday ? 'Today' : day.day}
          </p>
          <p className="text-xs font-bold text-slate-600 mt-0.5">{day.date}</p>
        </div>
        {day.status === 'completed' && (
          <CheckCircle2 size={16} className="text-[#2E7D32]" />
        )}
        {day.rain_expected ? (
          <CloudRain size={16} className="text-blue-400" />
        ) : (
          <Sun size={16} className="text-[#F9A826]" />
        )}
      </div>

      {/* Irrigate decision */}
      <div className={`rounded-xl px-3 py-2 border text-center ${statusColors[day.status]}`}>
        <p className="text-[11px] font-extrabold">
          {day.irrigate ? `${day.water_mm} mm` : 'No Irrigation'}
        </p>
      </div>

      {/* Rain info */}
      {day.rain_expected && (
        <div className="flex items-center gap-1.5 text-[10px] font-bold text-blue-500">
          <Droplets size={11} />
          <span>Rain: {day.rain_mm ?? '—'} mm expected</span>
        </div>
      )}
    </div>
  );
};
