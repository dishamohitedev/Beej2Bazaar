import React, { useState, useEffect } from 'react';
import api from '../../services/api';
import { IrrigationStatusCard } from '../../components/cards/IrrigationStatusCard';
import { ScheduleCard } from '../../components/cards/ScheduleCard';
import { WeatherSummaryCard } from '../../components/cards/WeatherSummaryCard';
import { CropInfoCard } from '../../components/cards/CropInfoCard';
import { ExplanationCard } from '../../components/cards/ExplanationCard';
import { ArrowLeft, Droplets, Loader2, Play, Square, Check } from 'lucide-react';
import { IrrigationPageData, IrrigationToday } from '../../types';

interface IrrigationPageProps {
  onBackToDashboard: () => void;
}

export const IrrigationPage: React.FC<IrrigationPageProps> = ({ onBackToDashboard }) => {
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState<IrrigationPageData | null>(null);
  const [pumpStatus, setPumpStatus] = useState<'pending' | 'watering' | 'completed' | 'skipped'>('pending');
  const [actionLoading, setActionLoading] = useState(false);

  const fetchIrrigationDetails = async () => {
    setLoading(true);
    try {
      // 1. Fetch Schedule & Weather
      const scheduleRes = await api.get('/api/irrigation/schedule');
      const s = scheduleRes.data;

      // 2. Fetch Profile to get crop name
      const profileRes = await api.get('/api/profile/me');
      const prof = profileRes.data;

      const cropsRes = await api.get('/api/crop/all');
      const allCrops = cropsRes.data;
      const currentCrop = allCrops.find((c: any) => c.id === prof.current_crop_id);
      const cropName = currentCrop ? currentCrop.crop_name : 'Sorghum';

      // 3. Fetch Pump/Status log for today
      const statusRes = await api.get('/api/irrigation/status');
      const currentStatus = statusRes.data;
      setPumpStatus(currentStatus.status || 'pending');

      // 4. Format into page data shape
      const formattedData: IrrigationPageData = {
        today: {
          irrigate: s.today.irrigate,
          water_mm: s.today.water_mm,
          reason: s.today.reason || currentStatus.reason || 'Calculated using FAO-56 Penman-Monteith.',
        },
        next_irrigation: s.next_irrigation || 'N/A',
        schedule: s.schedule.map((item: any) => {
          const dateObj = new Date(item.date);
          const dayName = dateObj.toLocaleDateString('en-US', { weekday: 'long' });
          const formattedDate = dateObj.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
          return {
            date: formattedDate,
            day: dayName,
            irrigate: item.irrigate,
            water_mm: item.water_mm,
            rain_expected: item.water_mm === 0,
            status: item.date === new Date().toISOString().split('T')[0] ? currentStatus.status : (item.irrigate ? 'pending' : 'skipped'),
          };
        }),
        weather: {
          temperature: Math.round(s.weather?.temp_max || 28),
          humidity: Math.round(s.weather?.relative_humidity || 74),
          rain_probability: s.weather?.precipitation > 0 ? 90 : 10,
          wind_speed: Math.round(s.weather?.wind_speed || 14),
        },
        crop: {
          name: cropName,
          growth_stage: prof.growth_stage || 'Vegetative',
          water_requirement: s.today.water_mm > 5 ? 'High' : s.today.water_mm > 2 ? 'Medium' : 'Low',
          soil_type: prof.soil_type || 'Black Cotton Soil',
        },
        explanation: s.explanation || 'Smart scheduling active.'
      };

      setData(formattedData);
    } catch (error) {
      console.error('Failed to load smart irrigation data', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchIrrigationDetails();
  }, []);

  const handleStartPump = async () => {
    setActionLoading(true);
    try {
      const res = await api.post('/api/irrigation/start');
      setPumpStatus(res.data.status);
    } catch (err) {
      console.error('Failed to start pump', err);
    } finally {
      setActionLoading(false);
    }
  };

  const handleCompletePump = async () => {
    setActionLoading(true);
    try {
      const res = await api.post('/api/irrigation/complete');
      setPumpStatus(res.data.status);
    } catch (err) {
      console.error('Failed to stop pump', err);
    } finally {
      setActionLoading(false);
    }
  };

  if (loading || !data) {
    return (
      <div className="flex flex-col items-center justify-center py-24 gap-3">
        <Loader2 className="animate-spin text-[#2E7D32]" size={36} />
        <span className="text-xs font-bold text-slate-400 uppercase tracking-widest">
          Calculating Irrigation Model...
        </span>
      </div>
    );
  }

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
      <IrrigationStatusCard today={data.today} next_irrigation={data.next_irrigation} />

      {/* Section 1.5 — Interactive Pump Controller */}
      {data.today.irrigate && (
        <div className="bg-white rounded-[24px] p-6 border border-[#2e7d32]/5 shadow-elevation flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className={`h-12 w-12 rounded-2xl flex items-center justify-center shrink-0 ${
              pumpStatus === 'watering'
                ? 'bg-blue-50 text-blue-500 animate-pulse'
                : pumpStatus === 'completed'
                  ? 'bg-emerald-50 text-emerald-500'
                  : 'bg-slate-50 text-slate-400'
            }`}>
              <Droplets size={22} />
            </div>
            <div>
              <h3 className="text-sm font-black text-slate-800">Drip Irrigation Pump</h3>
              <p className="text-[10px] text-slate-400 font-bold uppercase tracking-wider mt-0.5">
                Current State: <span className={
                  pumpStatus === 'watering' ? 'text-blue-500' : pumpStatus === 'completed' ? 'text-emerald-500' : 'text-slate-500'
                }>{pumpStatus}</span>
              </p>
            </div>
          </div>

          <div className="w-full sm:w-auto">
            {pumpStatus === 'pending' && (
              <button
                onClick={handleStartPump}
                disabled={actionLoading}
                className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-5 py-3 bg-[#2E7D32] hover:bg-[#256428] text-white rounded-2xl text-xs font-black uppercase tracking-wider shadow-sm transition-all cursor-pointer"
              >
                {actionLoading ? <Loader2 size={14} className="animate-spin" /> : <Play size={14} />}
                <span>Turn On Water Pump</span>
              </button>
            )}

            {pumpStatus === 'watering' && (
              <button
                onClick={handleCompletePump}
                disabled={actionLoading}
                className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-5 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-2xl text-xs font-black uppercase tracking-wider shadow-sm transition-all cursor-pointer"
              >
                {actionLoading ? <Loader2 size={14} className="animate-spin" /> : <Square size={14} />}
                <span>Turn Off Pump (Done)</span>
              </button>
            )}

            {pumpStatus === 'completed' && (
              <div className="inline-flex items-center gap-1.5 px-4 py-2 bg-emerald-50 text-emerald-600 border border-emerald-100 rounded-full text-xs font-bold">
                <Check size={14} />
                <span>Irrigated Successfully Today</span>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Section 2 — 7-Day schedule */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-base font-black text-slate-800">7-Day Irrigation Schedule</h2>
          <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">FAO-56</span>
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-7 gap-3">
          {data.schedule.map((day, index) => (
            <ScheduleCard key={day.date} day={day} isToday={index === 0} />
          ))}
        </div>
      </div>

      {/* Section 3 & 4 — Weather + Crop (side by side on desktop) */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        <WeatherSummaryCard weather={data.weather} />
        <CropInfoCard crop={data.crop} />
      </div>

      {/* Section 5 — AI Explanation */}
      <ExplanationCard explanation={data.explanation} />
    </div>
  );
};

export default IrrigationPage;
