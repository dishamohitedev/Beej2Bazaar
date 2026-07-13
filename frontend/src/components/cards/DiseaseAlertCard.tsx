import React from 'react';
import { Card } from '../ui/Card';
import { DiseaseAlert } from '../../types';
import { AlertTriangle, ShieldCheck } from 'lucide-react';
import { Badge } from '../ui/Badge';

interface DiseaseAlertCardProps {
  alerts: DiseaseAlert[];
  delay?: number;
  onScanCrop?: () => void;
}

export const DiseaseAlertCard: React.FC<DiseaseAlertCardProps> = ({ alerts, delay = 0, onScanCrop }) => {
  if (alerts.length === 0) return null;
  const activeAlert = alerts[0];

  const getThreatVariant = (level: string) => {
    switch (level) {
      case 'high':
        return 'danger';
      case 'medium':
        return 'accent';
      default:
        return 'neutral';
    }
  };

  return (
    <Card delay={delay} className="border border-red-100 bg-gradient-to-br from-white to-red-50/20 relative">
      <div className="flex justify-between items-start mb-4">
        <h2 className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Pest & Disease Warnings</h2>
        <Badge variant={getThreatVariant(activeAlert.threatLevel)}>{activeAlert.threatLevel} severity</Badge>
      </div>

      <div className="flex items-start gap-3 mt-2">
        <div className="h-9 w-9 rounded-xl bg-[#D32F2F]/10 flex items-center justify-center text-[#D32F2F] shrink-0 mt-0.5">
          <AlertTriangle size={18} />
        </div>
        <div>
          <h3 className="text-base font-extrabold text-slate-800 leading-tight">
            {activeAlert.diseaseName} on {activeAlert.cropName}s
          </h3>
          <p className="text-xs text-slate-500 font-semibold mt-1">
            Detected <span className="text-[#D32F2F] font-bold">{activeAlert.distanceKm} km</span> from your fields.
          </p>
        </div>
      </div>

      {/* Spray suggestion box */}
      <div className="mt-4 p-3 bg-red-500/[0.03] border border-red-500/10 rounded-2xl">
        <h4 className="text-[10px] font-bold uppercase tracking-wider text-red-700 flex items-center gap-1.5">
          <ShieldCheck size={12} />
          <span>Recommended Treatment Plan</span>
        </h4>
        <p className="text-xs font-semibold text-slate-600 leading-relaxed mt-1">
          {activeAlert.actionPlan}
        </p>
      </div>

      <div className="mt-4 pt-3 border-t border-slate-100 flex justify-between items-center text-xs">
        <span className="text-slate-400 font-semibold">1 more regional alert</span>
        <button 
          onClick={onScanCrop}
          className="font-bold text-[#D32F2F] hover:underline cursor-pointer"
        >
          Scan Your Crop →
        </button>
      </div>
    </Card>
  );
};
