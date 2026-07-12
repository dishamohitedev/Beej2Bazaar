import React from 'react';
import { Card } from '../ui/Card';
import { WeatherData } from '../../types';
import { Sun, Droplets, Wind, Compass, CloudRain } from 'lucide-react';

interface WeatherCardProps {
  data: WeatherData;
  delay?: number;
}

export const WeatherCard: React.FC<WeatherCardProps> = ({ data, delay = 0 }) => {
  return (
    <Card delay={delay} className="col-span-1 md:col-span-2 overflow-hidden bg-gradient-to-br from-white to-[#F7FAF4] relative">
      {/* Decorative sun flare gradient */}
      <div className="absolute top-[-30px] right-[-30px] w-48 h-48 bg-[#F9A826]/10 rounded-full blur-3xl pointer-events-none" />

      <div className="flex justify-between items-start mb-6">
        <div>
          <h2 className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Weather</h2>
          <p className="text-sm font-bold text-[#2E7D32] mt-0.5">{data.location}</p>
        </div>
        <div className="h-10 w-10 rounded-2xl bg-[#F9A826]/10 flex items-center justify-center text-[#F9A826]">
          <Sun size={24} />
        </div>
      </div>

      <div className="flex items-baseline gap-2 mb-6">
        <span className="text-5xl font-black tracking-tighter text-slate-900">{data.temperature}°</span>
        <span className="text-sm font-bold text-slate-500 capitalize">{data.condition}</span>
      </div>

      {/* Grid of Weather stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 border-t border-slate-100 pt-6">
        <div className="flex items-center gap-3">
          <div className="h-8 w-8 rounded-xl bg-blue-50 flex items-center justify-center text-blue-500">
            <Droplets size={16} />
          </div>
          <div className="flex flex-col leading-none">
            <span className="text-[9px] text-slate-400 font-bold uppercase tracking-wider">Humidity</span>
            <span className="text-sm font-extrabold text-slate-800 mt-0.5">{data.humidity}%</span>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="h-8 w-8 rounded-xl bg-[#2e7d32]/5 flex items-center justify-center text-[#2e7d32]">
            <Wind size={16} />
          </div>
          <div className="flex flex-col leading-none">
            <span className="text-[9px] text-slate-400 font-bold uppercase tracking-wider">Wind</span>
            <span className="text-sm font-extrabold text-slate-800 mt-0.5">{data.windSpeed} km/h</span>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="h-8 w-8 rounded-xl bg-[#F9A826]/10 flex items-center justify-center text-[#F9A826]">
            <Compass size={16} />
          </div>
          <div className="flex flex-col leading-none">
            <span className="text-[9px] text-slate-400 font-bold uppercase tracking-wider">UV Index</span>
            <span className="text-sm font-extrabold text-slate-800 mt-0.5">{data.uvIndex} / 10</span>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="h-8 w-8 rounded-xl bg-[#4CAF50]/10 flex items-center justify-center text-[#4CAF50]">
            <CloudRain size={16} />
          </div>
          <div className="flex flex-col leading-none">
            <span className="text-[9px] text-slate-400 font-bold uppercase tracking-wider">Precip.</span>
            <span className="text-sm font-extrabold text-slate-800 mt-0.5">{data.precipitationProbability}%</span>
          </div>
        </div>
      </div>

      {/* Advisory Message */}
      <div className="mt-5 bg-[#2E7D32]/5 border border-[#2E7D32]/10 rounded-2xl p-3.5 flex gap-3 items-start">
        <span className="text-sm leading-none">💡</span>
        <p className="text-xs text-[#2E7D32] font-semibold leading-relaxed">
          {data.recommendationText}
        </p>
      </div>
    </Card>
  );
};
