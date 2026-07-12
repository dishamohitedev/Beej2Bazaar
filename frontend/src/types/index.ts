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
