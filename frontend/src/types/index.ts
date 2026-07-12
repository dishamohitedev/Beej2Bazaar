export interface WeatherData {
  location: string;
  temperature: number;
  humidity: number;
  windSpeed: number;
  uvIndex: number;
  precipitationProbability: number; // percentage
  condition: 'sunny' | 'rainy' | 'cloudy' | 'stormy';
  recommendationText: string;
}

export interface CurrentCropData {
  cropName: string;
  stageName: string;
  daysToHarvest: number;
  plantedDate: string;
  currentSoilMoisture: number; // percentage
  targetSoilMoisture: number; // percentage
}

export interface CropSuggestion {
  id: string;
  cropName: string;
  matchPercentage: number;
  expectedRevenue: string; // e.g. "₹55,000 / acre"
  marketTrend: 'up' | 'down' | 'stable';
}

export interface IrrigationData {
  cropName: string;
  scheduledWateringTimes: string[];
  status: 'pending' | 'watering' | 'done';
  soilMoistureThreshold: number; // percentage
}

export interface DiseaseAlert {
  id: string;
  cropName: string;
  diseaseName: string;
  threatLevel: 'low' | 'medium' | 'high';
  distanceKm: number;
  actionPlan: string;
}

export interface MandiRate {
  id: string;
  cropName: string;
  marketName: string;
  pricePerQuintal: number;
  priceChange: number; // e.g. +150 or -50
  trend: 'up' | 'down' | 'stable';
}

export interface CommunityPost {
  id: string;
  authorName: string;
  avatarUrl?: string;
  role: 'Expert' | 'Farmer' | 'Trader';
  content: string;
  likesCount: number;
  repliesCount: number;
  tag: string;
}

export interface FarmerProfile {
  name: string;
  location: string;
  soilType: string;
  farmSizeAcres: number;
  district: string;
  state: string;
}

export interface CropRecommendationDetail {
  id: string;
  cropName: string;
  matchPercentage: number;
  expectedProfitPerAcre: number;
  marketPricePerQuintal: number;
  waterRequirementMm: number;
  growingSeason: string;
  sowingWindow: string;
  factors: {
    soilMoisture: string;
    soilPh: string;
    temperatureRange: string;
    marketDemand: string;
  };
  geminiExplanation: string;
}

export interface IrrigationToday {
  irrigate: boolean;
  water_mm: number;
  reason: string;
}

export interface IrrigationDaySchedule {
  date: string;
  day: string;
  irrigate: boolean;
  water_mm: number;
  rain_expected: boolean;
  rain_mm?: number;
  status: 'completed' | 'pending' | 'skipped';
}

export interface IrrigationWeather {
  temperature: number;
  humidity: number;
  rain_probability: number;
  wind_speed: number;
}

export interface IrrigationCrop {
  name: string;
  growth_stage: string;
  water_requirement: 'Low' | 'Medium' | 'High';
  soil_type: string;
}

export interface IrrigationPageData {
  today: IrrigationToday;
  next_irrigation: string;
  schedule: IrrigationDaySchedule[];
  weather: IrrigationWeather;
  crop: IrrigationCrop;
  explanation: string;
}
