import React from 'react';
import { Card } from '../ui/Card';
import { MapPin, MessageSquare, AlertCircle } from 'lucide-react';

interface NearbyAlertCardProps {
  reportsCount: number;
  district: string;
  affectedCrop: string;
  onViewCommunityClick?: () => void;
  delay?: number;
}

export const NearbyAlertCard: React.FC<NearbyAlertCardProps> = ({
  reportsCount,
  district,
  affectedCrop,
  onViewCommunityClick,
  delay = 0
}) => {
  return (
    <Card delay={delay} className="border border-purple-100 bg-gradient-to-br from-white to-purple-50/10 relative overflow-hidden">
      {/* Decorative community/chat circle blur */}
      <div className="absolute top-[-30px] right-[-30px] w-36 h-36 bg-purple-500/5 rounded-full blur-2xl pointer-events-none" />

      <div className="flex justify-between items-start mb-4">
        <div>
          <h2 className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Regional Alerts</h2>
          <p className="text-sm font-bold text-purple-700 mt-0.5">Nearby Disease outbreaks</p>
        </div>
        <div className="h-10 w-10 rounded-2xl bg-purple-50 text-purple-650 flex items-center justify-center">
          <AlertCircle size={20} />
        </div>
      </div>

      <div className="space-y-4">
        {/* Info panel */}
        <div className="flex items-center gap-3.5 p-4 rounded-2xl bg-slate-50 border border-slate-100/50">
          <div className="h-10 w-10 rounded-xl bg-purple-500/10 text-purple-650 flex items-center justify-center shrink-0">
            <MapPin size={20} />
          </div>
          <div className="flex flex-col min-w-0">
            <span className="text-[9px] font-bold text-slate-450 uppercase tracking-wider">Reports in {district}</span>
            <span className="text-sm font-black text-slate-800 mt-0.5">
              {reportsCount} active cases
            </span>
          </div>
        </div>

        {/* Affected details */}
        <div className="flex justify-between items-center text-xs font-semibold px-1 text-slate-500">
          <span>Target Crop:</span>
          <span className="font-extrabold text-slate-700">{affectedCrop}</span>
        </div>

        {/* View Discussion button */}
        <button
          onClick={onViewCommunityClick}
          className="w-full mt-2 py-3 bg-purple-50 hover:bg-purple-100/80 text-purple-700 rounded-2xl text-[11px] font-black uppercase tracking-wider transition-colors flex items-center justify-center gap-2 cursor-pointer border border-purple-100"
        >
          <MessageSquare size={14} />
          <span>View Community Discussion</span>
        </button>
      </div>
    </Card>
  );
};
