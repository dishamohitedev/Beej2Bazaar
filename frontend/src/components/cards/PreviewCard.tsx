import React from 'react';
import { Card } from '../ui/Card';
import { RefreshCw, Trash2, ShieldAlert, Cpu } from 'lucide-react';
import { motion } from 'framer-motion';

interface PreviewCardProps {
  imageUrl: string;
  isAnalyzing: boolean;
  onClear: () => void;
  onAnalyze?: () => void;
  delay?: number;
}

export const PreviewCard: React.FC<PreviewCardProps> = ({
  imageUrl,
  isAnalyzing,
  onClear,
  onAnalyze,
  delay = 0
}) => {
  return (
    <Card delay={delay} className="overflow-hidden border border-slate-100 bg-white relative">
      <div className="flex justify-between items-start mb-4">
        <div>
          <h2 className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Leaf Preview</h2>
          <p className="text-sm font-bold text-slate-800 mt-0.5">Image uploaded successfully</p>
        </div>
        {!isAnalyzing && (
          <button 
            onClick={onClear}
            className="h-8 w-8 rounded-xl bg-red-50 hover:bg-red-100 transition-colors flex items-center justify-center text-red-500 cursor-pointer"
            title="Delete Image"
          >
            <Trash2 size={16} />
          </button>
        )}
      </div>

      {/* Image Container */}
      <div className="relative aspect-video rounded-2xl overflow-hidden bg-slate-900 border border-slate-100 flex items-center justify-center">
        <img 
          src={imageUrl} 
          alt="Uploaded Crop Leaf" 
          className={`w-full h-full object-cover transition-opacity duration-500 ${isAnalyzing ? 'opacity-70 blur-[1px]' : 'opacity-100'}`}
        />

        {/* Scanning Animation */}
        {isAnalyzing && (
          <div className="absolute inset-0 flex flex-col items-center justify-center bg-black/45">
            {/* The laser scanning line */}
            <motion.div 
              initial={{ top: '0%' }}
              animate={{ top: '98%' }}
              transition={{ 
                duration: 2, 
                repeat: Infinity, 
                repeatType: 'reverse', 
                ease: 'easeInOut' 
              }}
              className="absolute left-0 right-0 h-1 bg-gradient-to-r from-transparent via-[#2E7D32] to-transparent shadow-[0_0_12px_#2E7D32] z-10"
            />
            
            {/* Overlay loading stats */}
            <div className="z-20 flex flex-col items-center gap-2 bg-white/95 rounded-2xl px-5 py-3.5 shadow-soft-lg backdrop-blur-md">
              <Cpu className="text-[#2E7D32] animate-spin" size={20} />
              <span className="text-[10px] font-black uppercase tracking-wider text-[#2E7D32]">
                Running Leaf Diagnostics...
              </span>
            </div>
          </div>
        )}
      </div>

      {/* Interactive controls */}
      {!isAnalyzing && onAnalyze && (
        <div className="mt-4 flex gap-3">
          <button
            onClick={onClear}
            className="flex-1 py-3 bg-slate-50 hover:bg-slate-100 border border-slate-200 text-slate-600 rounded-2xl text-xs font-black uppercase tracking-wider transition-colors flex items-center justify-center gap-2 cursor-pointer"
          >
            <RefreshCw size={14} />
            <span>Retake</span>
          </button>
          
          <button
            onClick={onAnalyze}
            className="flex-[2] py-3 bg-[#2E7D32] hover:bg-[#256428] text-white rounded-2xl text-xs font-black uppercase tracking-wider transition-colors flex items-center justify-center gap-2 shadow-sm cursor-pointer"
          >
            <Cpu size={14} />
            <span>Analyze Plant Health</span>
          </button>
        </div>
      )}
    </Card>
  );
};
