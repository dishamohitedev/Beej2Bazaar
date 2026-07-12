import React from 'react';
import { IrrigationPageData } from '../../types';
import { IrrigationStatusCard } from '../../components/cards/IrrigationStatusCard';
import { ScheduleCard } from '../../components/cards/ScheduleCard';
import { WeatherSummaryCard } from '../../components/cards/WeatherSummaryCard';
import { CropInfoCard } from '../../components/cards/CropInfoCard';
import { ExplanationCard } from '../../components/cards/ExplanationCard';
import { ArrowLeft, Droplets } from 'lucide-react';

interface IrrigationPageProps {
  onBackToDashboard: () => void;
}

const mockIrrigationData: IrrigationPageData = {
  today: {
    irrigate: true,
    water_mm: 5.4,
    reason: 'Crop evapotranspiration (ETc) exceeds forecast rainfall. Soybean is in the flowering stage where water stress can severely reduce yield.',
  },
  next_irrigation: 'Thursday',
  schedule: [
    {
      date: 'Mon, Jul 14',
      day: 'Monday',
      irrigate: true,
      water_mm: 5.4,
      rain_expected: false,
      status: 'completed',
    },
    {
      date: 'Tue, Jul 15',
      day: 'Tuesday',
      irrigate: false,
      water_mm: 0,
      rain_expected: true,
      rain_mm: 8,
      status: 'skipped',
    },
    {
      date: 'Wed, Jul 16',
      day: 'Wednesday',
      irrigate: false,
      water_mm: 0,
      rain_expected: true,
      rain_mm: 4,
      status: 'skipped',
    },
    {
      date: 'Thu, Jul 17',
      day: 'Thursday',
      irrigate: true,
      water_mm: 4.8,
      rain_expected: false,
      status: 'pending',
    },
    {
      date: 'Fri, Jul 18',
      day: 'Friday',
      irrigate: false,
      water_mm: 0,
      rain_expected: false,
      status: 'pending',
    },
    {
      date: 'Sat, Jul 19',
      day: 'Saturday',
      irrigate: true,
      water_mm: 5.1,
      rain_expected: false,
      status: 'pending',
    },
    {
      date: 'Sun, Jul 20',
      day: 'Sunday',
      irrigate: false,
      water_mm: 0,
      rain_expected: true,
      rain_mm: 6,
      status: 'pending',
    },
  ],
  weather: {
    temperature: 28,
    humidity: 74,
    rain_probability: 10,
    wind_speed: 14,
  },
  crop: {
    name: 'Soybean (JS 335)',
    growth_stage: 'Flowering',
    water_requirement: 'Medium',
    soil_type: 'Black Cotton Soil',
  },
  explanation:
    'The crop is currently in the flowering stage — the most water-sensitive phase of soybean development. Since forecast rainfall for the next 72 hours is below the crop evapotranspiration threshold of 5.4 mm (computed using FAO-56 Penman-Monteith), irrigation is strongly recommended today. Delaying irrigation during this phase can reduce pod formation by 20-35%. Soil moisture was last recorded at 41%, which is below the field capacity threshold of 65% for black cotton soil.',
};

export const IrrigationPage: React.FC<IrrigationPageProps> = ({ onBackToDashboard }) => {
  return (
    <div className="space-y-6">
      {/* Page header */}
      <div className="flex items-start justify-between gap-4">
        <div>
          <button
            onClick={onBackToDashboard}
            className="inline-flex items-center gap-1.5 text-xs font-bold text-[#2E7D32] hover:text-[#256428] transition-colors cursor-pointer mb-3"
          >
            <ArrowLeft size={14} />
            Back to Home
          </button>
          <h1 className="text-2xl font-black text-slate-900 tracking-tight flex items-center gap-2">
            <Droplets size={22} className="text-blue-500" />
            Smart Irrigation
          </h1>
          <p className="text-xs font-semibold text-slate-400 mt-1">
            Scientific irrigation schedule generated using FAO-56 methodology
          </p>
        </div>
        <div className="shrink-0 text-[10px] font-bold text-slate-500 bg-white px-3.5 py-1.5 rounded-full border border-slate-100 shadow-sm">
          WME · Active
        </div>
      </div>

      {/* Section 1 — Today's status */}
      <IrrigationStatusCard today={mockIrrigationData.today} next_irrigation={mockIrrigationData.next_irrigation} />

      {/* Section 2 — 7-Day schedule */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-base font-black text-slate-800">7-Day Irrigation Schedule</h2>
          <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">FAO-56</span>
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-7 gap-3">
          {mockIrrigationData.schedule.map((day, index) => (
            <ScheduleCard key={day.date} day={day} isToday={index === 0} />
          ))}
        </div>
      </div>

      {/* Section 3 & 4 — Weather + Crop (side by side on desktop) */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        <WeatherSummaryCard weather={mockIrrigationData.weather} />
        <CropInfoCard crop={mockIrrigationData.crop} />
      </div>

      {/* Section 5 — AI Explanation */}
      <ExplanationCard explanation={mockIrrigationData.explanation} />
    </div>
  );
};
