import React from 'react';
import { Card } from '../ui/Card';
import { Badge } from '../ui/Badge';
import { AlertOctagon, Info } from 'lucide-react';

interface SeverityCardProps {
  severity: 'Low' | 'Medium' | 'High';
  delay?: number;
}

export const SeverityCard: React.FC<SeverityCardProps> = ({
  severity,
  delay = 0
}) => {
  const getSeverityConfig = () => {
    switch (severity) {
      case 'High':
        return {
          variant: 'danger' as const,
          bgColor: 'bg-[#D32F2F]/10',
          textColor: 'text-[#D32F2F]',
          borderColor: 'border-[#D32F2F]/20',
          indicatorColor: 'bg-[#D32F2F]',
          description: 'Immediate action required. High threat of rapid infection spreading to nearby fields and crops.',
          meterValue: 100
        };
      case 'Medium':
        return {
          variant: 'accent' as const,
          bgColor: 'bg-[#F9A826]/10',
          textColor: 'text-[#D97706]',
          borderColor: 'border-[#F9A826]/20',
          indicatorColor: 'bg-[#F9A826]',
          description: 'Active monitoring and localized chemical/organic application suggested. Threat is moderate but manageable.',
          meterValue: 60
        };
      default:
        return {
          variant: 'secondary' as const,
          bgColor: 'bg-[#4CAF50]/10',
          textColor: 'text-[#2E7D32]',
          borderColor: 'border-[#4CAF50]/20',
          indicatorColor: 'bg-[#4CAF50]',
          description: 'Low threat level. Routine cultural practices and pruning should resolve symptoms.',
          meterValue: 30
        };
    }
  };

  const config = getSeverityConfig();

  return (
    <Card delay={delay} className="border border-slate-100 bg-white relative">
      <div className="flex justify-between items-start mb-6">
        <div>
          <h2 className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Threat Level</h2>
          <p className="text-sm font-bold text-slate-800 mt-0.5">Crop Infection Severity</p>
        </div>
        <div className={`h-10 w-10 rounded-2xl ${config.bgColor} flex items-center justify-center ${config.textColor}`}>
          <AlertOctagon size={20} />
        </div>
      </div>

      <div className="space-y-4">
        {/* Severity Label Display */}
        <div className="flex items-center justify-between pb-3 border-b border-slate-100">
          <span className="text-xs text-slate-500 font-bold uppercase tracking-wide">Severity Rating</span>
          <Badge variant={config.variant}>{severity}</Badge>
        </div>

        {/* Severity Meter (Radial/Linear bar style) */}
        <div>
          <div className="flex justify-between text-[10px] text-slate-400 font-bold uppercase tracking-wider mb-1.5">
            <span>Low</span>
            <span>Medium</span>
            <span>High</span>
          </div>
          <div className="w-full bg-slate-100 h-2.5 rounded-full overflow-hidden flex gap-0.5">
            <div className={`h-full flex-1 rounded-l-full ${config.meterValue >= 30 ? 'bg-[#4CAF50]' : 'bg-slate-200'}`} />
            <div className={`h-full flex-1 ${config.meterValue >= 60 ? 'bg-[#F9A826]' : 'bg-slate-200'}`} />
            <div className={`h-full flex-1 rounded-r-full ${config.meterValue >= 100 ? 'bg-[#D32F2F]' : 'bg-slate-200'}`} />
          </div>
        </div>

        {/* Advisory details */}
        <div className="mt-4 p-3.5 bg-slate-50 rounded-2xl border border-slate-100/50 flex gap-3 items-start">
          <Info size={16} className="text-slate-400 shrink-0 mt-0.5" />
          <p className="text-xs font-semibold text-slate-500 leading-relaxed">
            {config.description}
          </p>
        </div>
      </div>
    </Card>
  );
};
