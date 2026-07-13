import React from 'react';
import { Card } from '../ui/Card';
import { ShieldCheck, CheckCircle2 } from 'lucide-react';

interface TreatmentCardProps {
  treatment: string;
  delay?: number;
}

export const TreatmentCard: React.FC<TreatmentCardProps> = ({
  treatment,
  delay = 0
}) => {
  // Split treatment recommendations by periods to render distinct action steps
  const actionSteps = treatment
    .split('.')
    .map(step => step.trim())
    .filter(step => step.length > 0);

  return (
    <Card delay={delay} className="border border-slate-100 bg-white relative">
      <div className="flex justify-between items-start mb-5">
        <div>
          <h2 className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Treatment Plan</h2>
          <p className="text-sm font-bold text-slate-800 mt-0.5">Recommended Actions</p>
        </div>
        <div className="h-10 w-10 rounded-2xl bg-emerald-50 text-[#2E7D32] flex items-center justify-center">
          <ShieldCheck size={20} />
        </div>
      </div>

      <div className="space-y-4">
        {/* Render split list items */}
        {actionSteps.length > 0 ? (
          <div className="flex flex-col gap-3">
            {actionSteps.map((step, idx) => (
              <div 
                key={idx} 
                className="flex items-start gap-3 p-3 bg-slate-50 rounded-xl border border-slate-100 hover:bg-slate-100/40 transition-colors"
              >
                <div className="h-5 w-5 rounded-full bg-emerald-50 text-[#2E7D32] flex items-center justify-center shrink-0 mt-0.5">
                  <CheckCircle2 size={13} className="stroke-[2.5px]" />
                </div>
                <p className="text-xs font-semibold text-slate-650 leading-relaxed">
                  {step}.
                </p>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-xs font-semibold text-slate-600 leading-relaxed">
            {treatment}
          </p>
        )}
      </div>
    </Card>
  );
};
