import React, { useRef, useState } from 'react';
import { Card } from '../ui/Card';
import { Camera, UploadCloud, Leaf, Loader2 } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

interface UploadCardProps {
  onImageSelected: (file: File | string, isMock?: boolean) => void;
  onSelectMockScenario: (scenarioId: string) => void;
  delay?: number;
}

export const UploadCard: React.FC<UploadCardProps> = ({ 
  onImageSelected, 
  onSelectMockScenario,
  delay = 0 
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isDragActive, setIsDragActive] = useState(false);
  const [showMockOptions, setShowMockOptions] = useState(false);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setIsDragActive(true);
    } else if (e.type === "dragleave") {
      setIsDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      onImageSelected(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      onImageSelected(e.target.files[0]);
    }
  };

  const triggerFileSelect = () => {
    fileInputRef.current?.click();
  };

  return (
    <Card delay={delay} className="overflow-hidden border border-slate-100/50 bg-gradient-to-br from-white to-[#F7FAF4] relative">
      <div className="absolute top-[-30px] right-[-30px] w-48 h-48 bg-[#2E7D32]/5 rounded-full blur-3xl pointer-events-none" />
      
      <div className="flex justify-between items-start mb-6">
        <div>
          <h2 className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Diagnosis Upload</h2>
          <p className="text-sm font-bold text-[#2E7D32] mt-0.5">Select a crop leaf image for scan</p>
        </div>
        <div className="h-10 w-10 rounded-2xl bg-[#2E7D32]/10 flex items-center justify-center text-[#2E7D32]">
          <Leaf size={20} className="animate-pulse" />
        </div>
      </div>

      {/* Hidden native input */}
      <input 
        type="file" 
        ref={fileInputRef} 
        onChange={handleFileChange} 
        accept="image/*" 
        className="hidden" 
      />

      {/* Drag & Drop Area */}
      <motion.div 
        onDragEnter={handleDrag}
        onDragOver={handleDrag}
        onDragLeave={handleDrag}
        onDrop={handleDrop}
        onClick={triggerFileSelect}
        whileHover={{ scale: 1.005 }}
        whileTap={{ scale: 0.995 }}
        className={`border-2 border-dashed rounded-[20px] p-8 flex flex-col items-center justify-center text-center cursor-pointer transition-all duration-350 ${
          isDragActive 
            ? 'border-[#2E7D32] bg-[#2E7D32]/5 shadow-subtle' 
            : 'border-slate-200 hover:border-[#2E7D32]/40 hover:bg-[#2E7D32]/[0.01]'
        }`}
      >
        <div className="h-14 w-14 rounded-full bg-slate-50 border border-slate-100 flex items-center justify-center text-[#2E7D32] shadow-sm mb-4">
          <UploadCloud size={28} />
        </div>
        <p className="text-xs font-bold text-slate-700">Drag & drop your leaf photo here</p>
        <p className="text-[10px] text-slate-400 font-semibold mt-1">Supports JPEG, PNG up to 10MB</p>
      </motion.div>

      {/* Action Buttons */}
      <div className="grid grid-cols-2 gap-3 mt-4">
        <button
          onClick={() => setShowMockOptions(true)}
          className="py-3.5 bg-slate-50 border border-slate-200/80 hover:bg-slate-100 hover:border-slate-300 text-slate-700 rounded-2xl text-[11px] font-black uppercase tracking-wider transition-colors flex items-center justify-center gap-2 cursor-pointer"
        >
          <Camera size={14} className="text-[#2E7D32]" />
          <span>Take Photo</span>
        </button>

        <button
          onClick={triggerFileSelect}
          className="py-3.5 bg-[#2E7D32] hover:bg-[#256428] text-white rounded-2xl text-[11px] font-black uppercase tracking-wider transition-colors flex items-center justify-center gap-2 shadow-sm cursor-pointer"
        >
          <UploadCloud size={14} />
          <span>Upload Image</span>
        </button>
      </div>

      {/* Simulated Quick Diagnostics (Mock Selector) */}
      <AnimatePresence>
        {showMockOptions && (
          <motion.div 
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="mt-5 border-t border-slate-100 pt-4 overflow-hidden"
          >
            <div className="flex justify-between items-center mb-2">
              <span className="text-[9px] font-bold text-slate-400 uppercase tracking-wider">Simulated Camera Feeds</span>
              <button 
                onClick={() => setShowMockOptions(false)} 
                className="text-[9px] font-bold text-[#2E7D32] hover:underline cursor-pointer"
              >
                Hide
              </button>
            </div>
            <div className="flex flex-col gap-2">
              <button 
                onClick={() => {
                  onSelectMockScenario('scenario_1');
                  setShowMockOptions(false);
                }}
                className="w-full p-3 bg-white border border-[#D32F2F]/15 hover:bg-red-50/20 text-left rounded-xl flex items-center justify-between cursor-pointer"
              >
                <div className="flex items-center gap-2">
                  <span className="h-2 w-2 rounded-full bg-[#D32F2F] animate-pulse" />
                  <span className="text-xs font-bold text-slate-700">Tomato leaf (Late Blight)</span>
                </div>
                <span className="text-[9px] font-bold text-slate-400">Scan →</span>
              </button>
              <button 
                onClick={() => {
                  onSelectMockScenario('scenario_2');
                  setShowMockOptions(false);
                }}
                className="w-full p-3 bg-white border border-[#F9A826]/15 hover:bg-amber-50/20 text-left rounded-xl flex items-center justify-between cursor-pointer"
              >
                <div className="flex items-center gap-2">
                  <span className="h-2 w-2 rounded-full bg-[#F9A826] animate-pulse" />
                  <span className="text-xs font-bold text-slate-700">Onion leaf (Purple Blotch)</span>
                </div>
                <span className="text-[9px] font-bold text-slate-400">Scan →</span>
              </button>
              <button 
                onClick={() => {
                  onSelectMockScenario('scenario_3');
                  setShowMockOptions(false);
                }}
                className="w-full p-3 bg-white border border-[#2E7D32]/15 hover:bg-green-50/20 text-left rounded-xl flex items-center justify-between cursor-pointer"
              >
                <div className="flex items-center gap-2">
                  <span className="h-2 w-2 rounded-full bg-[#2E7D32] animate-pulse" />
                  <span className="text-xs font-bold text-slate-700">Cotton leaf (Curl Virus)</span>
                </div>
                <span className="text-[9px] font-bold text-slate-400">Scan →</span>
              </button>
              <button 
                onClick={() => {
                  onSelectMockScenario('scenario_4');
                  setShowMockOptions(false);
                }}
                className="w-full p-3 bg-white border border-[#4CAF50]/15 hover:bg-emerald-50/20 text-left rounded-xl flex items-center justify-between cursor-pointer"
              >
                <div className="flex items-center gap-2">
                  <span className="h-2 w-2 rounded-full bg-[#4CAF50] animate-pulse" />
                  <span className="text-xs font-bold text-slate-700">Rice leaf (Rice Blast)</span>
                </div>
                <span className="text-[9px] font-bold text-slate-400">Scan →</span>
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </Card>
  );
};
