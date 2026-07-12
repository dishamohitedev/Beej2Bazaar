import React, { useState } from 'react';
import { Card } from '../ui/Card';
import { IrrigationData } from '../../types';
import { Droplet, Clock, Power } from 'lucide-react';
import { Badge } from '../ui/Badge';

interface IrrigationCardProps {
  data: IrrigationData;
  delay?: number;
}

export const IrrigationCard: React.FC<IrrigationCardProps> = ({ data, delay = 0 }) => {
  const [watering, setWatering] = useState(false);

  return (
    <Card delay={delay} className="flex flex-col justify-between">
      <div>
        <div className="flex justify-between items-start mb-4">
          <h2 className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Watering Scheduler</h2>
          <Badge variant={watering ? 'primary' : 'neutral'}>
            {watering ? 'Running' : data.status}
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

      <div className="mt-5">
        <button
          onClick={() => setWatering(!watering)}
          className={`w-full flex items-center justify-center gap-2 rounded-2xl py-3 px-4 text-xs font-bold transition-all duration-200 cursor-pointer ${
            watering 
              ? 'bg-[#D32F2F] hover:bg-[#b71c1c] text-white shadow-sm'
              : 'bg-[#2E7D32] hover:bg-[#256428] text-white shadow-sm'
          }`}
        >
          <Power size={14} className={watering ? 'animate-pulse' : ''} />
          <span>{watering ? 'Stop Drip Valve' : 'Start Drip Valve'}</span>
        </button>
      </div>
    </Card>
  );
};
