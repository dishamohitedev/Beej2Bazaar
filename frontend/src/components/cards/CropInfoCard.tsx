import React from 'react';
import { IrrigationCrop } from '../../types';
import { Sprout, FlaskConical, Gauge, Layers } from 'lucide-react';

interface CropInfoCardProps {
  crop: IrrigationCrop;
}

const waterReqColor = {
  Low: 'text-[#2E7D32] bg-[#2E7D32]/8 border-[#2E7D32]/20',
  Medium: 'text-[#F9A826] bg-[#F9A826]/10 border-[#F9A826]/20',
  High: 'text-[#D32F2F] bg-[#D32F2F]/8 border-[#D32F2F]/20',
};

export const CropInfoCard: React.FC<CropInfoCardProps> = ({ crop }) => {
  return (
    <div className="rounded-[24px] bg-white border border-slate-100 p-5 shadow-[0_4px_20px_rgba(0,0,0,0.04)]">
      <div className="flex items-center justify-between mb-4">
        <div>
          <p className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Active Crop</p>
          <h3 className="text-lg font-black text-slate-800 tracking-tight mt-0.5">Crop Information</h3>
        </div>
        <div className="h-8 w-8 rounded-xl bg-[#2E7D32]/10 border border-[#2E7D32]/20 flex items-center justify-center">
          <Sprout size={16} className="text-[#2E7D32]" />
        </div>
      </div>

      <div className="space-y-3">
        {/* Crop name */}
        <div className="flex items-center justify-between p-3.5 rounded-2xl bg-slate-50 border border-slate-100/50">
          <div className="flex items-center gap-2.5 text-slate-500">
            <Sprout size={15} />
            <span className="text-xs font-bold">Current Crop</span>
          </div>
          <span className="text-xs font-extrabold text-slate-800">{crop.name}</span>
        </div>

        {/* Growth stage */}
        <div className="flex items-center justify-between p-3.5 rounded-2xl bg-slate-50 border border-slate-100/50">
          <div className="flex items-center gap-2.5 text-slate-500">
            <Gauge size={15} />
            <span className="text-xs font-bold">Growth Stage</span>
          </div>
          <span className="text-xs font-extrabold text-[#2E7D32]">{crop.growth_stage}</span>
        </div>

        {/* Water requirement */}
        <div className="flex items-center justify-between p-3.5 rounded-2xl bg-slate-50 border border-slate-100/50">
          <div className="flex items-center gap-2.5 text-slate-500">
            <FlaskConical size={15} />
            <span className="text-xs font-bold">Water Requirement</span>
          </div>
          <span className={`text-[10px] font-extrabold px-2.5 py-1 rounded-full border ${waterReqColor[crop.water_requirement]}`}>
            {crop.water_requirement}
          </span>
        </div>

        {/* Soil type */}
        <div className="flex items-center justify-between p-3.5 rounded-2xl bg-slate-50 border border-slate-100/50">
          <div className="flex items-center gap-2.5 text-slate-500">
            <Layers size={15} />
            <span className="text-xs font-bold">Soil Type</span>
          </div>
          <span className="text-xs font-extrabold text-slate-800">{crop.soil_type}</span>
        </div>
      </div>
    </div>
  );
};
