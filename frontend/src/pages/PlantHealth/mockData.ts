import { PlantHealthData } from '../../types';

export interface MockDiseaseScenario {
  id: string;
  cropName: string;
  diseaseName: string;
  imageFileName: string;
  imagePlaceholderUrl: string; // for mock rendering
  data: PlantHealthData;
}

export const mockDiseaseScenarios: MockDiseaseScenario[] = [
  {
    id: 'scenario_1',
    cropName: 'Tomato',
    diseaseName: 'Late Blight',
    imageFileName: 'tomato_late_blight.jpg',
    imagePlaceholderUrl: 'https://images.unsplash.com/photo-1592417817098-8f3d6eb19675?w=600&auto=format&fit=crop&q=80',
    data: {
      prediction: 'Tomato Late Blight (Phytophthora infestans)',
      confidence: 94.5,
      severity: 'High',
      treatment: 'Apply copper-based fungicides or Chlorothalonil immediately. Prune lower leaves to improve air circulation and prevent soil splashing. Destroy heavily infected plant debris (do not compost). Shift from overhead sprinkler watering to drip irrigation to keep leaf canopy dry.',
      community_alerts: {
        reports_count: 14,
        district: 'Nashik',
        affected_crop: 'Tomato'
      },
      government_advisory: 'The Maharashtra State Agricultural Extension has issued an alert for Late Blight in Nashik district following persistent wet spells. Farmers are advised to initiate preventative sprays of Metalaxyl-M or Mancozeb and report local outbreak levels to their Gram Panchayat representative.'
    }
  },
  {
    id: 'scenario_2',
    cropName: 'Onion',
    diseaseName: 'Purple Blotch',
    imageFileName: 'onion_purple_blotch.jpg',
    imagePlaceholderUrl: 'https://images.unsplash.com/photo-1618512417743-af78db0fca8e?w=600&auto=format&fit=crop&q=80',
    data: {
      prediction: 'Onion Purple Blotch (Alternaria porri)',
      confidence: 82.0,
      severity: 'Medium',
      treatment: 'Spray Mancozeb (0.25%) or Tebuconazole + Trifloxystrobin formulation. Maintain spacing between onion rows. Ensure proper field drainage to avoid standing water. Apply nitrogenous fertilizers in balanced doses, as excess nitrogen can aggravate disease progression.',
      community_alerts: {
        reports_count: 8,
        district: 'Nashik',
        affected_crop: 'Onion'
      },
      government_advisory: 'District Advisory: Moderate threat of Purple Blotch reported in Niphad and Lasalgaon subdivisions. Ensure seed treatment before future plantings and monitor leaf tips during morning surveys.'
    }
  },
  {
    id: 'scenario_3',
    cropName: 'Cotton',
    diseaseName: 'Leaf Curl Virus',
    imageFileName: 'cotton_leaf_curl.jpg',
    imagePlaceholderUrl: 'https://images.unsplash.com/photo-1594900119853-2fdb303fdf53?w=600&auto=format&fit=crop&q=80',
    data: {
      prediction: 'Cotton Leaf Curl Virus (CLCuV)',
      confidence: 88.0,
      severity: 'High',
      treatment: 'Focus on controlling the whitefly vector (Bemisia tabaci) using systemic insecticides like Acetamiprid or Neem-based oil sprays. Uproot and burn virus-infected plants immediately to prevent secondary spread. Grow whitefly-tolerant varieties in the next crop rotation.',
      community_alerts: {
        reports_count: 22,
        district: 'Wardha',
        affected_crop: 'Cotton'
      },
      government_advisory: 'State Cotton Board Notification: Whitefly counts have crossed threshold values in East Maharashtra. Farmers are urged to implement community-wide vector control protocols and avoid late sowing cycles.'
    }
  },
  {
    id: 'scenario_4',
    cropName: 'Rice',
    diseaseName: 'Rice Blast',
    imageFileName: 'rice_blast.jpg',
    imagePlaceholderUrl: 'https://images.unsplash.com/photo-1594900119853-2fdb303fdf53?w=600&auto=format&fit=crop&q=80',
    data: {
      prediction: 'Rice Blast (Magnaporthe oryzae)',
      confidence: 91.2,
      severity: 'High',
      treatment: 'Spray Tricyclazole (0.06%) or Isoprothiolane immediately. Avoid excess application of nitrogenous fertilizers, as it increases leaf blast severity. Keep fields flooded to moderate leaf temperature and reduce spore germination. Use certified disease-free seeds for the next season.',
      community_alerts: {
        reports_count: 18,
        district: 'Nashik',
        affected_crop: 'Rice'
      },
      government_advisory: 'District Krishi Alert: Active pockets of Rice Blast have been detected in low-lying terraces. Farmers are advised to maintain critical field water levels and apply chemical protection when leaf lesions are first sighted.'
    }
  }
];
