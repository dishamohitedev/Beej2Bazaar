import React from 'react';
import { ArrowLeft, MessageSquare, Sparkles } from 'lucide-react';

interface FeedHeaderProps {
  onBackToDashboard: () => void;
}

export const FeedHeader: React.FC<FeedHeaderProps> = ({ onBackToDashboard }) => {
  return (
    <div className="flex items-start justify-between gap-4">
      <div>
        <button
          onClick={onBackToDashboard}
          className="inline-flex items-center gap-1.5 text-xs font-bold text-[#2E7D32] hover:text-[#256428] transition-colors cursor-pointer mb-3"
        >
          <ArrowLeft size={14} />
          <span>Back to Home</span>
        </button>
        <h1 className="text-2xl font-black text-slate-900 tracking-tight flex items-center gap-2">
          <MessageSquare size={22} className="text-purple-600" />
          AgriFeed
        </h1>
        <p className="text-xs font-semibold text-slate-400 mt-1">
          Connect with farmers around you
        </p>
      </div>
      <div className="shrink-0 text-[10px] font-bold text-purple-700 bg-white px-3.5 py-1.5 rounded-full border border-slate-100 shadow-sm flex items-center gap-1">
        <Sparkles size={11} className="text-purple-500 animate-pulse" />
        <span>Realtime Feed</span>
      </div>
    </div>
  );
};
