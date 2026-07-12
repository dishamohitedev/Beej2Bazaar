import React from 'react';
import { Card } from '../ui/Card';
import { CropRecommendationDetail } from '../../types';
import { Scale, X, Droplet, DollarSign, Calendar, Compass } from 'lucide-react';

interface CompareCardProps {
  cropA: CropRecommendationDetail;
  cropB: CropRecommendationDetail;
  onClose: () => void;
}

export const CompareCard: React.FC<CompareCardProps> = ({ cropA, cropB, onClose }) => {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm">
      <Card className="w-full max-w-2xl bg-white border border-[#2e7d32]/10 shadow-soft-lg flex flex-col justify-between max-h-[90vh] overflow-y-auto">
        <div>
          {/* Header */}
          <div className="flex justify-between items-center pb-4 border-b border-slate-100 mb-6">
            <div className="flex items-center gap-2 text-[#2E7D32]">
              <Scale size={20} />
              <h3 className="text-lg font-black tracking-tight text-slate-800">Crop Comparison Panel</h3>
            </div>
            <button
              onClick={onClose}
              className="h-8 w-8 rounded-full bg-slate-50 border border-slate-100 flex items-center justify-center text-slate-400 hover:text-slate-650 hover:bg-slate-100 cursor-pointer"
            >
              <X size={16} />
            </button>
          </div>

          {/* Comparison Matrix Table */}
          <div className="grid grid-cols-3 gap-2 text-center text-xs pb-3 border-b border-slate-100/60 mb-3">
            <div className="text-left font-bold text-slate-400 uppercase tracking-wider text-[9px] pt-1">Parameters</div>
            <div className="font-extrabold text-[#2E7D32] truncate">{cropA.cropName}</div>
            <div className="font-extrabold text-blue-600 truncate">{cropB.cropName}</div>
          </div>

          <div className="space-y-4">
            {/* Match Rate */}
            <div className="grid grid-cols-3 gap-2 items-center text-xs pb-2.5 border-b border-slate-50">
              <div className="text-left text-slate-500 font-bold">Match Rate</div>
              <div className="font-extrabold text-[#2E7D32] bg-[#2E7D32]/5 p-2 rounded-xl border border-[#2E7D32]/10">
                {cropA.matchPercentage}% Match
              </div>
              <div className="font-extrabold text-blue-650 bg-blue-500/5 p-2 rounded-xl border border-blue-500/10">
                {cropB.matchPercentage}% Match
              </div>
            </div>

            {/* Expected Profit */}
            <div className="grid grid-cols-3 gap-2 items-center text-xs pb-2.5 border-b border-slate-50">
              <div className="text-left text-slate-500 font-bold flex items-center gap-1">
                <DollarSign size={13} className="text-slate-400" />
                <span>Profit / Acre</span>
              </div>
              <div className="font-extrabold text-slate-800">
                ₹{cropA.expectedProfitPerAcre.toLocaleString()}
              </div>
              <div className="font-extrabold text-slate-800">
                ₹{cropB.expectedProfitPerAcre.toLocaleString()}
              </div>
            </div>

            {/* Mandi Rate */}
            <div className="grid grid-cols-3 gap-2 items-center text-xs pb-2.5 border-b border-slate-50">
              <div className="text-left text-slate-500 font-bold">Mandi Price</div>
              <div className="font-bold text-slate-700">
                ₹{cropA.marketPricePerQuintal.toLocaleString()}/q
              </div>
              <div className="font-bold text-slate-700">
                ₹{cropB.marketPricePerQuintal.toLocaleString()}/q
              </div>
            </div>

            {/* Sowing Window */}
            <div className="grid grid-cols-3 gap-2 items-center text-xs pb-2.5 border-b border-slate-50">
              <div className="text-left text-slate-500 font-bold flex items-center gap-1">
                <Calendar size={13} className="text-slate-400" />
                <span>Sowing Time</span>
              </div>
              <div className="font-bold text-slate-700 text-[11px]">
                {cropA.sowingWindow}
              </div>
              <div className="font-bold text-slate-700 text-[11px]">
                {cropB.sowingWindow}
              </div>
            </div>

            {/* Water requirement */}
            <div className="grid grid-cols-3 gap-2 items-center text-xs pb-2.5 border-b border-slate-50">
              <div className="text-left text-slate-500 font-bold flex items-center gap-1">
                <Droplet size={13} className="text-slate-400" />
                <span>Water Demand</span>
              </div>
              <div className="font-bold text-slate-700">
                {cropA.waterRequirementMm} mm
              </div>
              <div className="font-bold text-slate-700">
                {cropB.waterRequirementMm} mm
              </div>
            </div>

            {/* Soil pH suitability */}
            <div className="grid grid-cols-3 gap-2 items-center text-xs pb-2.5 border-b border-slate-50">
              <div className="text-left text-slate-500 font-bold flex items-center gap-1">
                <Compass size={13} className="text-slate-400" />
                <span>Soil pH Limit</span>
              </div>
              <div className="font-bold text-slate-700">
                {cropA.factors.soilPh}
              </div>
              <div className="font-bold text-slate-700">
                {cropB.factors.soilPh}
              </div>
            </div>

            {/* Soil Moisture suitability */}
            <div className="grid grid-cols-3 gap-2 items-center text-xs pb-2.5 border-b border-slate-50">
              <div className="text-left text-slate-500 font-bold">Soil Moisture</div>
              <div className="font-bold text-slate-700">
                {cropA.factors.soilMoisture}
              </div>
              <div className="font-bold text-slate-700">
                {cropB.factors.soilMoisture}
              </div>
            </div>

            {/* Temp Range suitability */}
            <div className="grid grid-cols-3 gap-2 items-center text-xs">
              <div className="text-left text-slate-500 font-bold">Optimal Temp</div>
              <div className="font-bold text-slate-700">
                {cropA.factors.temperatureRange}
              </div>
              <div className="font-bold text-slate-700">
                {cropB.factors.temperatureRange}
              </div>
            </div>
          </div>
        </div>

        {/* Action Button */}
        <div className="mt-8 border-t border-slate-100 pt-4">
          <button
            onClick={onClose}
            className="w-full rounded-2xl bg-[#2E7D32] hover:bg-[#256428] py-3.5 px-4 text-xs font-bold text-white shadow-sm transition-all duration-200 cursor-pointer"
          >
            Done Comparing
          </button>
        </div>
      </Card>
    </div>
  );
};
