import React from 'react';
import { Card } from '../ui/Card';
import { IrrigationData } from '../../types';
import { Clock } from 'lucide-react';
import { Badge } from '../ui/Badge';

interface IrrigationCardProps {
  data: IrrigationData;
  delay?: number;
}

export const IrrigationCard: React.FC<IrrigationCardProps> = ({ data, delay = 0 }) => {

  return (
    <Card delay={delay}>
      <div>
        <div className="flex justify-between items-start mb-4">
          <h2 className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Watering Scheduler</h2>
          <Badge variant={data.status === 'watering' ? 'primary' : 'neutral'}>
            {data.status}
          </Badge>
        </div>

        <h3 className="text-lg font-black text-slate-800 tracking-tight">Today's Cycles</h3>
        <p className="text-xs text-slate-500 font-semibold mt-1">
          Target crop: <span className="text-slate-700 font-bold">{data.cropName}</span>
        </p>

        {/* Schedule times list */}
        <div className="mt-5 space-y-2.5">
          {data.scheduledWateringTimes.map((time, idx) => (
            <div key={idx} className="flex items-center justify-between p-2.5 bg-slate-50 rounded-xl border border-slate-100">
              <div className="flex items-center gap-2 text-xs font-bold text-slate-700">
                <Clock size={14} className="text-[#2E7D32]" />
                <span>{time}</span>
              </div>
              <span className="text-[10px] text-slate-400 font-bold uppercase tracking-wider">
                {idx === 0 && !watering ? 'Completed' : 'Pending'}
              </span>
            </div>
          ))}
        </div>

        <div className="mt-4 text-[10px] font-semibold text-slate-400">
          *Triggers automatically if moisture drops below <span className="text-[#2E7D32] font-bold">{data.soilMoistureThreshold}%</span>.
        </div>
      </div>
    </Card>
  );
};
