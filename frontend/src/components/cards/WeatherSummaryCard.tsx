import React from 'react';
import { IrrigationWeather } from '../../types';
import { Thermometer, Droplets, CloudRain, Wind } from 'lucide-react';

interface WeatherSummaryCardProps {
  weather: IrrigationWeather;
}

const WeatherMetric: React.FC<{ icon: React.ReactNode; label: string; value: string }> = ({ icon, label, value }) => (
  <div className="flex items-center gap-3 p-4 rounded-2xl bg-slate-50 border border-slate-100/50">
    <div className="h-9 w-9 rounded-xl bg-white border border-slate-100 flex items-center justify-center text-[#2E7D32] shadow-sm shrink-0">
      {icon}
    </div>
    <div>
      <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">{label}</p>
      <p className="text-sm font-extrabold text-slate-800 mt-0.5">{value}</p>
    </div>
  </div>
);

export const WeatherSummaryCard: React.FC<WeatherSummaryCardProps> = ({ weather }) => {
  return (
    <div className="rounded-[24px] bg-white border border-slate-100 p-5 shadow-[0_4px_20px_rgba(0,0,0,0.04)]">
      <div className="flex items-center justify-between mb-4">
        <div>
          <p className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Read Only</p>
          <h3 className="text-lg font-black text-slate-800 tracking-tight mt-0.5">Weather Summary</h3>
        </div>
        <div className="h-8 w-8 rounded-xl bg-[#F9A826]/10 border border-[#F9A826]/20 flex items-center justify-center">
          <Thermometer size={16} className="text-[#F9A826]" />
        </div>
      </div>
      <div className="grid grid-cols-2 gap-3">
        <WeatherMetric icon={<Thermometer size={16} />} label="Temperature" value={`${weather.temperature}°C`} />
        <WeatherMetric icon={<Droplets size={16} />} label="Humidity" value={`${weather.humidity}%`} />
        <WeatherMetric icon={<CloudRain size={16} />} label="Rain Probability" value={`${weather.rain_probability}%`} />
        <WeatherMetric icon={<Wind size={16} />} label="Wind Speed" value={`${weather.wind_speed} km/h`} />
      </div>
    </div>
  );
};
