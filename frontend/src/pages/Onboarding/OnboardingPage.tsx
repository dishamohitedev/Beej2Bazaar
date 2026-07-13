import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import api from '../../services/api';
import { Sprout, MapPin, Tractor, Calendar, ChevronRight, ChevronLeft, Loader2 } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

interface CropOption {
  id: string;
  crop_name: string;
  scientific_name: string;
  season: string;
}

export const OnboardingPage: React.FC = () => {
  const { user, submitOnboarding, logout } = useAuth();
  const [currentStep, setCurrentStep] = useState(1);
  const [crops, setCrops] = useState<CropOption[]>([]);
  const [loadingCrops, setLoadingCrops] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  // Form State
  const [fullName, setFullName] = useState(user?.name || '');
  const [language, setLanguage] = useState('Marathi');
  const [state, setState] = useState('Maharashtra');
  const [district, setDistrict] = useState('Nashik');
  const [taluka, setTaluka] = useState('Lasalgaon');
  const [village, setVillage] = useState('');
  
  const [farmSize, setFarmSize] = useState('2.0');
  const [soilType, setSoilType] = useState('Black Clay Soil (Regur)');
  const [irrigation, setIrrigation] = useState('Drip');
  const [selectedGoals, setSelectedGoals] = useState<string[]>(['Maximize Yield']);

  const [currentCropId, setCurrentCropId] = useState('');
  const [growthStage, setGrowthStage] = useState('Vegetative');
  const [sowingDate, setSowingDate] = useState('');
  const [expectedHarvest, setExpectedHarvest] = useState('');

  // Pre-load crops list from backend on mount
  useEffect(() => {
    const fetchCrops = async () => {
      setLoadingCrops(true);
      try {
        const response = await api.get('/api/crop/all');
        setCrops(response.data);
        if (response.data.length > 0) {
          setCurrentCropId(response.data[0].id);
        }
      } catch (err) {
        console.error('Failed to load crop dropdown data', err);
      } finally {
        setLoadingCrops(false);
      }
    };
    fetchCrops();
  }, []);

  const toggleGoal = (goal: string) => {
    if (selectedGoals.includes(goal)) {
      setSelectedGoals(selectedGoals.filter(g => g !== goal));
    } else {
      setSelectedGoals([...selectedGoals, goal]);
    }
  };

  const handleNext = () => {
    setError('');
    if (currentStep === 1) {
      if (!fullName.trim() || !state.trim() || !district.trim() || !taluka.trim() || !village.trim()) {
        setError('Please fill in all location details and name.');
        return;
      }
    }
    if (currentStep === 2) {
      const sizeVal = parseFloat(farmSize);
      if (isNaN(sizeVal) || sizeVal <= 0) {
        setError('Please enter a valid farm size greater than 0.');
        return;
      }
      if (selectedGoals.length === 0) {
        setError('Please select at least one farming goal.');
        return;
      }
    }
    setCurrentStep(prev => prev + 1);
  };

  const handleBack = () => {
    setCurrentStep(prev => prev - 1);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSubmitting(true);

    const payload = {
      full_name: fullName.trim(),
      language,
      state: state.trim(),
      district: district.trim(),
      taluka: taluka.trim(),
      village: village.trim(),
      farm_size: parseFloat(farmSize),
      farm_unit: 'acre',
      soil_type: soilType,
      irrigation,
      farming_goals: selectedGoals,
      current_crop_id: currentCropId || null,
      growth_stage: currentCropId ? growthStage : null,
      sowing_date: currentCropId && sowingDate ? sowingDate : null,
      expected_harvest: currentCropId && expectedHarvest ? expectedHarvest : null,
    };

    try {
      await submitOnboarding(payload);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Onboarding submission failed. Check your data and retry.');
    } finally {
      setSubmitting(false);
    }
  };

  const goalOptions = [
    'Maximize Yield',
    'Save Water / Reduce Costs',
    'Reduce Chemical Sprays',
    'Organic Cultivation',
    'Pest & Disease Security',
  ];

  const soilOptions = [
    'Black Clay Soil (Regur)',
    'Red Sandy Loam',
    'Laterite / Gravelly',
    'Alluvial / Loamy Silts',
    'Clay Loam',
  ];

  const irrigationOptions = [
    'Drip',
    'Sprinkler',
    'Borewell / Flood',
    'Canal Fed',
    'Rainfed Only',
  ];

  const growthStages = [
    'Sowing / Germination',
    'Vegetative Development',
    'Flowering',
    'Bulb Development',
    'Fruit Development / Ripening',
  ];

  return (
    <div className="min-h-screen bg-[#F7FAF4] py-8 px-4 sm:px-6 lg:px-8 flex flex-col justify-between">
      {/* Top Banner */}
      <header className="max-w-3xl mx-auto w-full flex items-center justify-between mb-8">
        <div className="flex items-center gap-2">
          <Sprout className="text-[#2E7D32]" size={24} />
          <span className="font-black text-slate-800 text-lg tracking-tight">BeejBazaar Onboarding</span>
        </div>
        <button
          onClick={logout}
          className="text-xs font-bold text-slate-400 hover:text-slate-600 transition-colors cursor-pointer"
        >
          Logout / Exit
        </button>
      </header>

      {/* Main Container */}
      <main className="max-w-3xl mx-auto w-full flex-1">
        {/* Progress Stepper */}
        <div className="flex items-center justify-between mb-8 max-w-md mx-auto px-4">
          {[1, 2, 3].map((num) => (
            <div key={num} className="flex items-center">
              <div className={`h-8 w-8 rounded-full flex items-center justify-center text-xs font-black transition-all ${
                currentStep === num 
                  ? 'bg-[#2E7D32] text-white ring-4 ring-[#2E7D32]/10 scale-110' 
                  : currentStep > num 
                    ? 'bg-[#2E7D32]/20 text-[#2E7D32]' 
                    : 'bg-white text-slate-400 border border-slate-100'
              }`}>
                {num}
              </div>
              {num < 3 && (
                <div className={`h-0.5 w-16 sm:w-24 mx-2 rounded-full transition-all ${
                  currentStep > num ? 'bg-[#2E7D32]' : 'bg-slate-200'
                }`} />
              )}
            </div>
          ))}
        </div>

        {/* Card Body */}
        <div className="bg-white rounded-3xl p-6 sm:p-8 border border-[#2e7d32]/5 shadow-elevation">
          <AnimatePresence mode="wait">
            {currentStep === 1 && (
              <motion.div
                key="step-1"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                transition={{ duration: 0.2 }}
                className="space-y-6"
              >
                <div className="flex items-center gap-3 border-b border-slate-100 pb-4">
                  <div className="p-2.5 bg-blue-50 text-blue-500 rounded-2xl">
                    <MapPin size={20} />
                  </div>
                  <div>
                    <h2 className="text-lg font-black text-slate-800">Location & Language</h2>
                    <p className="text-xs font-semibold text-slate-400">Tell us where your farm is located</p>
                  </div>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div className="space-y-1.5 col-span-2">
                    <label className="text-xs font-bold text-slate-400 uppercase tracking-wider">Farmer Name</label>
                    <input
                      type="text"
                      value={fullName}
                      onChange={(e) => setFullName(e.target.value)}
                      placeholder="e.g. Ramesh Patil"
                      className="w-full px-4 py-3 bg-slate-50/50 border border-slate-100 rounded-2xl text-slate-800 text-sm font-semibold focus:outline-none focus:ring-2 focus:ring-[#2E7D32]/25 focus:border-[#2E7D32]"
                    />
                  </div>

                  <div className="space-y-1.5">
                    <label className="text-xs font-bold text-slate-400 uppercase tracking-wider">Preferred Language</label>
                    <select
                      value={language}
                      onChange={(e) => setLanguage(e.target.value)}
                      className="w-full px-4 py-3 bg-slate-50/50 border border-slate-100 rounded-2xl text-slate-800 text-sm font-semibold focus:outline-none focus:ring-2 focus:ring-[#2E7D32]/25"
                    >
                      <option value="Marathi">मराठी (Marathi)</option>
                      <option value="Hindi">हिन्दी (Hindi)</option>
                      <option value="English">English</option>
                    </select>
                  </div>

                  <div className="space-y-1.5">
                    <label className="text-xs font-bold text-slate-400 uppercase tracking-wider">State</label>
                    <input
                      type="text"
                      value={state}
                      onChange={(e) => setState(e.target.value)}
                      className="w-full px-4 py-3 bg-slate-50/50 border border-slate-100 rounded-2xl text-slate-800 text-sm font-semibold focus:outline-none focus:ring-2 focus:ring-[#2E7D32]/25"
                    />
                  </div>

                  <div className="space-y-1.5">
                    <label className="text-xs font-bold text-slate-400 uppercase tracking-wider">District</label>
                    <input
                      type="text"
                      value={district}
                      onChange={(e) => setDistrict(e.target.value)}
                      className="w-full px-4 py-3 bg-slate-50/50 border border-slate-100 rounded-2xl text-slate-800 text-sm font-semibold focus:outline-none focus:ring-2 focus:ring-[#2E7D32]/25"
                    />
                  </div>

                  <div className="space-y-1.5">
                    <label className="text-xs font-bold text-slate-400 uppercase tracking-wider">Taluka / Sub-District</label>
                    <input
                      type="text"
                      value={taluka}
                      onChange={(e) => setTaluka(e.target.value)}
                      className="w-full px-4 py-3 bg-slate-50/50 border border-slate-100 rounded-2xl text-slate-800 text-sm font-semibold focus:outline-none focus:ring-2 focus:ring-[#2E7D32]/25"
                    />
                  </div>

                  <div className="space-y-1.5 col-span-2">
                    <label className="text-xs font-bold text-slate-400 uppercase tracking-wider">Village</label>
                    <input
                      type="text"
                      value={village}
                      onChange={(e) => setVillage(e.target.value)}
                      placeholder="e.g. Lasalgaon"
                      className="w-full px-4 py-3 bg-slate-50/50 border border-slate-100 rounded-2xl text-slate-800 text-sm font-semibold focus:outline-none focus:ring-2 focus:ring-[#2E7D32]/25"
                    />
                  </div>
                </div>
              </motion.div>
            )}

            {currentStep === 2 && (
              <motion.div
                key="step-2"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                transition={{ duration: 0.2 }}
                className="space-y-6"
              >
                <div className="flex items-center gap-3 border-b border-slate-100 pb-4">
                  <div className="p-2.5 bg-emerald-50 text-emerald-500 rounded-2xl">
                    <Tractor size={20} />
                  </div>
                  <div>
                    <h2 className="text-lg font-black text-slate-800">Farm details</h2>
                    <p className="text-xs font-semibold text-slate-400">Soil type, water source and primary targets</p>
                  </div>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
                  <div className="space-y-1.5">
                    <label className="text-xs font-bold text-slate-400 uppercase tracking-wider">Farm Size (Acres)</label>
                    <input
                      type="number"
                      step="0.1"
                      value={farmSize}
                      onChange={(e) => setFarmSize(e.target.value)}
                      className="w-full px-4 py-3 bg-slate-50/50 border border-slate-100 rounded-2xl text-slate-800 text-sm font-semibold focus:outline-none focus:ring-2 focus:ring-[#2E7D32]/25"
                    />
                  </div>

                  <div className="space-y-1.5">
                    <label className="text-xs font-bold text-slate-400 uppercase tracking-wider">Soil Type</label>
                    <select
                      value={soilType}
                      onChange={(e) => setSoilType(e.target.value)}
                      className="w-full px-4 py-3 bg-slate-50/50 border border-slate-100 rounded-2xl text-slate-800 text-sm font-semibold focus:outline-none focus:ring-2"
                    >
                      {soilOptions.map(opt => <option key={opt} value={opt}>{opt}</option>)}
                    </select>
                  </div>

                  <div className="space-y-1.5">
                    <label className="text-xs font-bold text-slate-400 uppercase tracking-wider">Irrigation Setup</label>
                    <select
                      value={irrigation}
                      onChange={(e) => setIrrigation(e.target.value)}
                      className="w-full px-4 py-3 bg-slate-50/50 border border-slate-100 rounded-2xl text-slate-800 text-sm font-semibold focus:outline-none focus:ring-2"
                    >
                      {irrigationOptions.map(opt => <option key={opt} value={opt}>{opt}</option>)}
                    </select>
                  </div>

                  <div className="space-y-2 col-span-2">
                    <label className="text-xs font-bold text-slate-400 uppercase tracking-wider block">Farming Goals</label>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                      {goalOptions.map(goal => (
                        <div
                          key={goal}
                          onClick={() => toggleGoal(goal)}
                          className={`px-4 py-3 rounded-2xl border text-xs font-bold cursor-pointer transition-all ${
                            selectedGoals.includes(goal)
                              ? 'bg-[#2E7D32]/10 border-[#2E7D32] text-[#2E7D32]'
                              : 'bg-slate-50/50 border-slate-100 text-slate-600 hover:border-slate-200'
                          }`}
                        >
                          {goal}
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </motion.div>
            )}

            {currentStep === 3 && (
              <motion.div
                key="step-3"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                transition={{ duration: 0.2 }}
                className="space-y-6"
              >
                <div className="flex items-center gap-3 border-b border-slate-100 pb-4">
                  <div className="p-2.5 bg-amber-50 text-amber-500 rounded-2xl">
                    <Calendar size={20} />
                  </div>
                  <div>
                    <h2 className="text-lg font-black text-slate-800">Current Crop Track (Optional)</h2>
                    <p className="text-xs font-semibold text-slate-400">Configure your active crop to activate trackers immediately</p>
                  </div>
                </div>

                {loadingCrops ? (
                  <div className="flex items-center justify-center py-12 gap-2 text-slate-400 text-sm font-bold">
                    <Loader2 className="animate-spin text-[#2E7D32]" size={20} />
                    <span>Loading crops repository...</span>
                  </div>
                ) : (
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div className="space-y-1.5 col-span-2">
                      <label className="text-xs font-bold text-slate-400 uppercase tracking-wider block">Active Crop</label>
                      <select
                        value={currentCropId}
                        onChange={(e) => setCurrentCropId(e.target.value)}
                        className="w-full px-4 py-3 bg-slate-50/50 border border-slate-100 rounded-2xl text-slate-800 text-sm font-semibold focus:outline-none"
                      >
                        <option value="">-- No Active Crop (Decide Later) --</option>
                        {crops.map(crop => (
                          <option key={crop.id} value={crop.id}>
                            {crop.crop_name} ({crop.season})
                          </option>
                        ))}
                      </select>
                    </div>

                    {currentCropId && (
                      <>
                        <div className="space-y-1.5">
                          <label className="text-xs font-bold text-slate-400 uppercase tracking-wider">Growth Stage</label>
                          <select
                            value={growthStage}
                            onChange={(e) => setGrowthStage(e.target.value)}
                            className="w-full px-4 py-3 bg-slate-50/50 border border-slate-100 rounded-2xl text-slate-800 text-sm font-semibold focus:outline-none"
                          >
                            {growthStages.map(stage => <option key={stage} value={stage}>{stage}</option>)}
                          </select>
                        </div>

                        <div className="space-y-1.5">
                          <label className="text-xs font-bold text-slate-400 uppercase tracking-wider">Sowing Date</label>
                          <input
                            type="date"
                            value={sowingDate}
                            onChange={(e) => setSowingDate(e.target.value)}
                            className="w-full px-4 py-3 bg-slate-50/50 border border-slate-100 rounded-2xl text-slate-800 text-sm font-semibold focus:outline-none"
                          />
                        </div>

                        <div className="space-y-1.5">
                          <label className="text-xs font-bold text-slate-400 uppercase tracking-wider">Expected Harvest Date</label>
                          <input
                            type="date"
                            value={expectedHarvest}
                            onChange={(e) => setExpectedHarvest(e.target.value)}
                            className="w-full px-4 py-3 bg-slate-50/50 border border-slate-100 rounded-2xl text-slate-800 text-sm font-semibold focus:outline-none"
                          />
                        </div>
                      </>
                    )}
                  </div>
                )}
              </motion.div>
            )}
          </AnimatePresence>

          {/* Alert Error Box */}
          {error && (
            <div className="mt-6 text-xs font-bold text-red-500 bg-red-50/50 border border-red-100/50 p-3.5 rounded-xl">
              {error}
            </div>
          )}

          {/* Navigation Controls */}
          <div className="flex items-center justify-between border-t border-slate-100 mt-8 pt-6">
            <button
              onClick={handleBack}
              disabled={currentStep === 1 || submitting}
              className={`inline-flex items-center gap-1.5 text-xs font-bold text-slate-400 hover:text-slate-600 transition-colors cursor-pointer disabled:opacity-0 disabled:cursor-default`}
            >
              <ChevronLeft size={16} />
              <span>Back</span>
            </button>

            {currentStep < 3 ? (
              <button
                onClick={handleNext}
                className="inline-flex items-center gap-1.5 px-5 py-3 bg-[#2E7D32] hover:bg-[#256428] text-white rounded-2xl text-xs font-black uppercase tracking-wider transition-colors shadow-sm cursor-pointer"
              >
                <span>Continue</span>
                <ChevronRight size={14} />
              </button>
            ) : (
              <button
                onClick={handleSubmit}
                disabled={submitting}
                className="inline-flex items-center gap-1.5 px-6 py-3 bg-[#2E7D32] hover:bg-[#256428] text-white rounded-2xl text-xs font-black uppercase tracking-wider transition-colors shadow-sm cursor-pointer disabled:opacity-75"
              >
                {submitting ? (
                  <>
                    <Loader2 size={14} className="animate-spin" />
                    <span>Completing Setup...</span>
                  </>
                ) : (
                  <>
                    <span>Submit & Finish</span>
                    <ChevronRight size={14} />
                  </>
                )}
              </button>
            )}
          </div>
        </div>
      </main>

      {/* Footer copyright */}
      <footer className="text-center text-[10px] font-bold text-slate-400 uppercase tracking-widest mt-8">
        BeejBazaar DECISION ENGINE v1.0.0
      </footer>
    </div>
  );
};

export default OnboardingPage;
