import React from 'react';
import { Card } from '../ui/Card';
import { CurrentCropData } from '../../types';
import { Calendar, Sprout } from 'lucide-react';
import { Badge } from '../ui/Badge';

interface CurrentCropCardProps {
  data: CurrentCropData;
  delay?: number;
}

export const CurrentCropCard: React.FC<CurrentCropCardProps> = ({ data, delay = 0 }) => {
  return (
    <Card delay={delay} className="flex flex-col justify-between">
      <div>
        <div className="flex justify-between items-start mb-4">
          <h2 className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Current Tracker</h2>
          <Badge variant="primary">Active</Badge>
        </div>

        <h3 className="text-xl font-black text-slate-800 tracking-tight">{data.cropName}</h3>
        <p className="text-xs text-slate-500 font-semibold mt-1 flex items-center gap-1.5">
          <span className="inline-block w-2 h-2 rounded-full bg-[#4CAF50] animate-ping" />
          Growth: <span className="text-[#2E7D32]">{data.stageName}</span>
        </p>

        <div className="mt-5 space-y-3">
          <div className="flex items-center gap-3">
            <div className="h-8 w-8 rounded-xl bg-slate-50 border border-slate-100 flex items-center justify-center text-slate-450">
              <Calendar size={15} />
            </div>
            <div className="flex flex-col">
              <span className="text-[9px] text-slate-400 font-bold uppercase tracking-wider">Harvest Countdown</span>
              <span className="text-sm font-extrabold text-slate-700">{data.daysToHarvest} days left</span>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="h-8 w-8 rounded-xl bg-slate-50 border border-slate-100 flex items-center justify-center text-slate-450">
              <Sprout size={15} />
            </div>
            <div className="flex flex-col">
              <span className="text-[9px] text-slate-400 font-bold uppercase tracking-wider">Planted Date</span>
              <span className="text-xs font-bold text-slate-600">{data.plantedDate}</span>
            </div>
          </div>
        </div>
      </div>

      <div className="mt-6 border-t border-slate-100 pt-4">
        <div className="flex justify-between items-center text-xs font-bold text-slate-500 mb-2">
          <span>Soil Moisture Status</span>
          <span className="text-[#2E7D32]">{data.currentSoilMoisture}% / {data.targetSoilMoisture}%</span>
        </div>
        <div className="h-2.5 w-full rounded-full bg-slate-100 overflow-hidden relative">
          <div 
            className="absolute top-0 bottom-0 w-0.5 bg-red-400 z-10"
            style={{ left: `${data.targetSoilMoisture}%` }}
          />
          <div 
            className="h-full rounded-full bg-gradient-to-r from-[#4CAF50] to-[#2E7D32]" 
            style={{ width: `${data.currentSoilMoisture}%` }} 
          />
        </div>
        <span className="text-[9px] font-semibold text-slate-400 mt-1.5 block">
          Current level is slightly below target. Watering advised.
        </span>
      </div>
    </Card>
  );
};
