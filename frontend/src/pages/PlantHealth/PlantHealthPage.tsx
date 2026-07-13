import React, { useState } from 'react';
import { ArrowLeft, HeartPulse, Loader2, Sparkles, RefreshCw } from 'lucide-react';
import { UploadCard } from '../../components/cards/UploadCard';
import { PreviewCard } from '../../components/cards/PreviewCard';
import { PredictionCard } from '../../components/cards/PredictionCard';
import { SeverityCard } from '../../components/cards/SeverityCard';
import { TreatmentCard } from '../../components/cards/TreatmentCard';
import { NearbyAlertCard } from '../../components/cards/NearbyAlertCard';
import { GovernmentAdvisoryCard } from '../../components/cards/GovernmentAdvisoryCard';
import { PlantHealthData } from '../../types';
import { mockDiseaseScenarios, MockDiseaseScenario } from './mockData';
import { motion, AnimatePresence } from 'framer-motion';

interface PlantHealthPageProps {
  currentCropName?: string;
  onBackToDashboard: () => void;
}

export const PlantHealthPage: React.FC<PlantHealthPageProps> = ({ currentCropName, onBackToDashboard }) => {
  const [status, setStatus] = useState<'idle' | 'uploading' | 'analyzing' | 'detected'>('idle');
  const [selectedImage, setSelectedImage] = useState<string | null>(null);
  const [predictionData, setPredictionData] = useState<PlantHealthData | null>(null);

  // Trigger analysis simulation
  const startAnalysis = (mockData: PlantHealthData) => {
    setStatus('analyzing');
    setTimeout(() => {
      setPredictionData(mockData);
      setStatus('detected');
    }, 2500); // 2.5s scanning simulation
  };

  // Callback when a user drags/drops or uploads a file
  const handleImageSelected = (file: File | string) => {
    setStatus('uploading');
    
    // Convert File to object URL for previewing, or use direct mock path if it is a string URL
    const previewUrl = typeof file === 'string' 
      ? file 
      : URL.createObjectURL(file);
      
    setTimeout(() => {
      setSelectedImage(previewUrl);
      
      // Dynamic matching based on crop name
      let selectedScenario = mockDiseaseScenarios[0].data; // Default: Tomato
      
      const cropLower = (currentCropName || '').toLowerCase();
      if (cropLower.includes('onion')) {
        const found = mockDiseaseScenarios.find(s => s.id === 'scenario_2');
        if (found) selectedScenario = found.data;
      } else if (cropLower.includes('cotton')) {
        const found = mockDiseaseScenarios.find(s => s.id === 'scenario_3');
        if (found) selectedScenario = found.data;
      } else if (cropLower.includes('rice') || cropLower.includes('sorghum')) {
        // Map Rice Blast for Rice/Sorghum
        const found = mockDiseaseScenarios.find(s => s.id === 'scenario_4');
        if (found) selectedScenario = found.data;
      }
      
      setStatus('uploading');
      // Transition from upload complete to interactive preview
      startAnalysis(selectedScenario);
    }, 1000);
  };

  // Callback when user selects a specific quick-simulate scenario
  const handleSelectMockScenario = (scenarioId: string) => {
    const scenario = mockDiseaseScenarios.find(s => s.id === scenarioId);
    if (scenario) {
      setSelectedImage(scenario.imagePlaceholderUrl);
      startAnalysis(scenario.data);
    }
  };

  const handleReset = () => {
    setStatus('idle');
    setSelectedImage(null);
    setPredictionData(null);
  };

  return (
    <div className="space-y-6 max-w-lg mx-auto pb-10">
      {/* Header section with back button */}
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
            <HeartPulse size={22} className="text-[#2E7D32]" />
            Plant Health
          </h1>
          <p className="text-xs font-semibold text-slate-400 mt-1">
            AI Assisted Disease Detection
          </p>
        </div>
        <div className="shrink-0 text-[10px] font-bold text-[#2E7D32] bg-white px-3.5 py-1.5 rounded-full border border-slate-100 shadow-sm flex items-center gap-1">
          <Sparkles size={11} className="text-amber-500 animate-pulse" />
          <span>GenAI Supported</span>
        </div>
      </div>

      {/* Main interactive state switcher */}
      <AnimatePresence mode="wait">
        {status === 'idle' && (
          <motion.div
            key="upload"
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -15 }}
            transition={{ duration: 0.3 }}
          >
            <UploadCard 
              onImageSelected={handleImageSelected} 
              onSelectMockScenario={handleSelectMockScenario} 
            />
          </motion.div>
        )}

        {(status === 'uploading' || status === 'analyzing') && selectedImage && (
          <motion.div
            key="scanning"
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -15 }}
            transition={{ duration: 0.3 }}
          >
            <PreviewCard 
              imageUrl={selectedImage} 
              isAnalyzing={true} 
              onClear={handleReset} 
            />
          </motion.div>
        )}

        {status === 'detected' && selectedImage && predictionData && (
          <motion.div
            key="results"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.4 }}
            className="space-y-6"
          >
            {/* Image Preview with reset controller */}
            <PreviewCard 
              imageUrl={selectedImage} 
              isAnalyzing={false} 
              onClear={handleReset} 
            />

            {/* Prediction and Severity details grid */}
            <div className="grid grid-cols-1 gap-5">
              <PredictionCard 
                diseaseName={predictionData.prediction} 
                confidence={predictionData.confidence} 
                delay={0.05}
              />
              
              <SeverityCard 
                severity={predictionData.severity} 
                delay={0.1}
              />
            </div>

            {/* Treatment recommendations */}
            <TreatmentCard 
              treatment={predictionData.treatment} 
              delay={0.15}
            />

            {/* Nearby disease reports */}
            <NearbyAlertCard 
              reportsCount={predictionData.community_alerts.reports_count}
              district={predictionData.community_alerts.district}
              affectedCrop={predictionData.community_alerts.affected_crop}
              onViewCommunityClick={onBackToDashboard} // simulate community navigation
              delay={0.2}
            />

            {/* Official Government Advisory */}
            <GovernmentAdvisoryCard 
              advisory={predictionData.government_advisory} 
              delay={0.25}
            />

            {/* Bottom Scan Another Crop action */}
            <motion.div 
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="pt-2"
            >
              <button
                onClick={handleReset}
                className="w-full py-3.5 bg-white border border-[#2E7D32]/25 hover:bg-[#2E7D32]/5 text-[#2E7D32] rounded-2xl text-xs font-black uppercase tracking-wider transition-colors flex items-center justify-center gap-2 cursor-pointer shadow-sm"
              >
                <RefreshCw size={14} />
                <span>Scan Another Crop</span>
              </button>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default PlantHealthPage;
