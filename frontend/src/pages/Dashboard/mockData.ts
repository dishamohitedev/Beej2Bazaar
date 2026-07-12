import { 
  WeatherData, 
  CurrentCropData, 
  CropSuggestion, 
  IrrigationData, 
  DiseaseAlert, 
  MandiRate, 
  CommunityPost,
  FarmerProfile 
} from '../../types';

export const mockFarmerProfile: FarmerProfile = {
  name: 'Ramesh Patil',
  location: 'Lasalgaon, Nashik',
  soilType: 'Black Clay Soil (Regur)',
  farmSizeAcres: 4.8,
  district: 'Nashik',
  state: 'Maharashtra',
};

export const mockWeatherData: WeatherData = {
  location: 'Lasalgaon, Nashik',
  temperature: 28,
  humidity: 65,
  windSpeed: 14,
  uvIndex: 5,
  precipitationProbability: 25,
  condition: 'sunny',
  recommendationText: 'Perfect weather for foliar nutrient sprays. Light evening showers expected.',
};

export const mockCurrentCropData: CurrentCropData = {
  cropName: 'Red Onion (N-53)',
  stageName: 'Bulb Development',
  daysToHarvest: 32,
  plantedDate: 'April 12, 2026',
  currentSoilMoisture: 58,
  targetSoilMoisture: 65,
};

export const mockCropSuggestions: CropSuggestion[] = [
  {
    id: 's_01',
    cropName: 'Soybean (JS 335)',
    matchPercentage: 96,
    expectedRevenue: '₹48,000 / Acre',
    marketTrend: 'up',
  },
  {
    id: 's_02',
    cropName: 'Bt Cotton (G-Cot 21)',
    matchPercentage: 88,
    expectedRevenue: '₹62,000 / Acre',
    marketTrend: 'up',
  },
  {
    id: 's_03',
    cropName: 'Sweet Maize',
    matchPercentage: 82,
    expectedRevenue: '₹35,000 / Acre',
    marketTrend: 'stable',
  },
];

export const mockIrrigationData: IrrigationData = {
  cropName: 'Red Onion (N-53)',
  scheduledWateringTimes: ['08:00 AM', '05:30 PM'],
  status: 'pending',
  soilMoistureThreshold: 45,
};

export const mockDiseaseAlerts: DiseaseAlert[] = [
  {
    id: 'a_01',
    cropName: 'Tomato',
    diseaseName: 'Early Blight',
    threatLevel: 'high',
    distanceKm: 3.2,
    actionPlan: 'Apply copper-based fungicides immediately. Avoid overhead sprinkler irrigation.',
  },
  {
    id: 'a_02',
    cropName: 'Onion',
    diseaseName: 'Purple Blotch',
    threatLevel: 'medium',
    distanceKm: 7.5,
    actionPlan: 'Monitor bulb necks for yellow spots. Spray Mancozeb if symptoms appear.',
  },
];

export const mockMandiRates: MandiRate[] = [
  {
    id: 'm_01',
    cropName: 'Onion (Red)',
    marketName: 'Lasalgaon Mandi',
    pricePerQuintal: 2850,
    priceChange: 150,
    trend: 'up',
  },
  {
    id: 'm_02',
    cropName: 'Tomato',
    marketName: 'Pimplas APMC',
    pricePerQuintal: 1900,
    priceChange: -80,
    trend: 'down',
  },
  {
    id: 'm_03',
    cropName: 'Soybean',
    marketName: 'Nashik APMC',
    pricePerQuintal: 4750,
    priceChange: 0,
    trend: 'stable',
  },
];

export const mockCommunityPost: CommunityPost = {
  id: 'p_01',
  authorName: 'Dr. Sudhir Tambe',
  role: 'Expert',
  avatarUrl: 'https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=100&auto=format&fit=crop&q=80',
  content: 'Seeing yellow spots on onion leaf tips in Nashik sub-district. Early signs of Purple Blotch due to current high humidity (65%+). Spraying Tebuconazole + Trifloxystrobin is recommended.',
  likesCount: 34,
  repliesCount: 9,
  tag: 'PestAlert',
};
