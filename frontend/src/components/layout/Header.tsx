import React from 'react';
import { Sun, CloudRain, Cloud, CloudLightning, MapPin } from 'lucide-react';
import { WeatherData, FarmerProfile } from '../../types';

interface HeaderProps {
  profile: FarmerProfile;
  weather: WeatherData;
}

export const Header: React.FC<HeaderProps> = ({ profile, weather }) => {
  const getWeatherIcon = (condition: string) => {
    switch (condition) {
      case 'sunny':
        return <Sun size={20} className="text-[#F9A826] animate-pulse" />;
      case 'rainy':
        return <CloudRain size={20} className="text-blue-400" />;
      case 'cloudy':
        return <Cloud size={20} className="text-slate-400" />;
      case 'stormy':
        return <CloudLightning size={20} className="text-purple-500" />;
      default:
        return <Sun size={20} className="text-[#F9A826]" />;
    }
  };

  return (
    <header className="sticky top-0 z-40 w-full border-b border-[#2e7d32]/5 bg-[#F7FAF4]/90 backdrop-blur-md px-4 py-4 md:px-6">
      <div className="mx-auto flex max-w-lg items-center justify-between md:max-w-5xl">
        <div className="flex flex-col">
          <span className="text-[10px] font-bold text-[#2E7D32] uppercase tracking-wider">
            Smart Agriculture Hub
          </span>
          <h1 className="text-xl font-extrabold tracking-tight text-slate-900 leading-tight">
            Good Morning, {profile.name.split(' ')[0]} 👋
          </h1>
          <div className="flex items-center gap-1 mt-0.5 text-slate-500">
            <MapPin size={12} className="text-[#2E7D32]" />
            <span className="text-xs font-semibold">{profile.location}</span>
          </div>
        </div>

        {/* Live Weather Indicator */}
        <div className="flex items-center gap-2 rounded-2xl bg-white border border-[#2e7d32]/5 px-3.5 py-2 shadow-sm">
          {getWeatherIcon(weather.condition)}
          <div className="flex flex-col items-start leading-none">
            <span className="text-sm font-extrabold text-slate-800">{weather.temperature}°C</span>
            <span className="text-[9px] font-bold text-slate-400 uppercase tracking-wider capitalize mt-0.5">
              {weather.condition}
            </span>
          </div>
        </div>
      </div>
    </header>
  );
};
