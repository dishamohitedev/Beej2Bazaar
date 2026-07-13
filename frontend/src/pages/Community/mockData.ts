import { PlantHealthData } from '../../types';
import sweetMaizeImg from './sweet_maize.png';

export interface FeedComment {
  id: string;
  authorName: string;
  avatarUrl?: string;
  role: 'Farmer' | 'Expert' | 'Trader' | 'Government Officer';
  content: string;
  timestamp: string;
}

export interface FeedPost {
  id: string;
  authorName: string;
  avatarUrl?: string;
  role: 'Farmer' | 'Expert' | 'Trader' | 'Government Officer';
  isVerified?: boolean;
  timestamp: string;
  postType: 'update' | 'question' | 'disease' | 'government' | 'market' | 'weather' | 'success' | 'tip';
  content: string;
  imageUrl?: string;
  likesCount: number;
  commentsCount: number;
  comments: FeedComment[];
  hasLiked?: boolean;
  // Specific details for special cards
  diseaseDetails?: {
    cropName: string;
    diseaseName: string;
    severity: 'Low' | 'Medium' | 'High';
    reportsCount: number;
    district: string;
  };
  marketDetails?: {
    cropName: string;
    marketName: string;
    pricePerQuintal: number;
    priceChange: number;
    trend: 'up' | 'down' | 'stable';
  };
  governmentDetails?: {
    issuingAuthority: string;
    advisoryLevel: 'Info' | 'Warning' | 'Critical';
    targetRegion: string;
  };
}

export const mockFeedPosts: FeedPost[] = [
  {
    id: 'post_1',
    authorName: 'Balasaheb Vikhe',
    avatarUrl: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=100&auto=format&fit=crop&q=80',
    role: 'Farmer',
    isVerified: true,
    timestamp: '2h ago',
    postType: 'update',
    content: 'Just finished sowing the new hybrid onion seeds (N-53) on 2 acres of land in Lasalgaon. The soil moisture looks perfect after the light showers yesterday. Praying for a steady monsoon this season! 🌱🌧️',
    likesCount: 24,
    commentsCount: 3,
    hasLiked: false,
    comments: [
      {
        id: 'c_11',
        authorName: 'Sanjay Patil',
        role: 'Farmer',
        content: 'Best of luck Balasaheb! Let us know how the germination rate turns out in a week.',
        timestamp: '1h ago'
      },
      {
        id: 'c_12',
        authorName: 'Dr. Ramesh G.',
        role: 'Expert',
        content: 'Ensure you maintain standard row-to-row spacing of 15 cm to prevent fungal issues later.',
        timestamp: '45m ago'
      }
    ]
  },
  {
    id: 'post_2',
    authorName: 'Dr. Sudhir Tambe',
    avatarUrl: 'https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=100&auto=format&fit=crop&q=80',
    role: 'Expert',
    isVerified: true,
    timestamp: '4h ago',
    postType: 'disease',
    content: 'ALERT: Rapid outbreak of Purple Blotch reported in onion nurseries in the Niphad block of Nashik. Spores are spreading fast due to 85%+ morning humidity levels. Apply prophylactic chemical sprays immediately.',
    likesCount: 42,
    commentsCount: 6,
    hasLiked: false,
    diseaseDetails: {
      cropName: 'Onion',
      diseaseName: 'Purple Blotch (Alternaria porri)',
      severity: 'High',
      reportsCount: 19,
      district: 'Nashik'
    },
    comments: [
      {
        id: 'c_21',
        authorName: 'Anil Deshmukh',
        role: 'Farmer',
        content: 'Which chemical is most effective right now, doctor? My crop is 40 days old.',
        timestamp: '3h ago'
      },
      {
        id: 'c_22',
        authorName: 'Dr. Sudhir Tambe',
        role: 'Expert',
        content: 'Anil, spray Tebuconazole 25.9% EC (1 ml/liter of water) or Mancozeb 75% WP (2.5 g/liter).',
        timestamp: '2h ago'
      }
    ]
  },
  {
    id: 'post_3',
    authorName: 'Ministry of Agriculture',
    avatarUrl: 'https://images.unsplash.com/photo-1593113598332-cd288d649433?w=100&auto=format&fit=crop&q=80',
    role: 'Government Officer',
    isVerified: true,
    timestamp: '5h ago',
    postType: 'government',
    content: 'The Department has approved a 50% subsidy on micro-irrigation sets (drip/sprinkler) for small and marginal farmers for the current financial year. Registration is active on the Mahadbt portal. Please submit applications before July 31.',
    likesCount: 56,
    commentsCount: 4,
    hasLiked: false,
    governmentDetails: {
      issuingAuthority: 'Krishi Vibhag, Maharashtra',
      advisoryLevel: 'Info',
      targetRegion: 'Maharashtra State'
    },
    comments: [
      {
        id: 'c_31',
        authorName: 'Vijay Kakade',
        role: 'Farmer',
        content: 'Is this subsidy available for leasehold land as well?',
        timestamp: '4h ago'
      }
    ]
  },
  {
    id: 'post_4',
    authorName: 'Lalit APMC Reporter',
    avatarUrl: 'https://images.unsplash.com/photo-1522075469751-3a6694fb2f61?w=100&auto=format&fit=crop&q=80',
    role: 'Trader',
    isVerified: true,
    timestamp: '6h ago',
    postType: 'market',
    content: 'Lasalgaon Mandi Onion prices see an upward bounce of ₹150/quintal due to lower arrivals and high export demand. Market sentiment remains bullish for the rest of the week.',
    likesCount: 38,
    commentsCount: 2,
    hasLiked: false,
    marketDetails: {
      cropName: 'Red Onion',
      marketName: 'Lasalgaon Mandi',
      pricePerQuintal: 2850,
      priceChange: 150,
      trend: 'up'
    },
    comments: [
      {
        id: 'c_41',
        authorName: 'Devidas More',
        role: 'Farmer',
        content: 'Excellent news. I will harvest my crop next week and bring it to the mandi.',
        timestamp: '5h ago'
      }
    ]
  },
  {
    id: 'post_5',
    authorName: 'Dnyaneshwar Shinde',
    avatarUrl: 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=100&auto=format&fit=crop&q=80',
    role: 'Farmer',
    isVerified: false,
    timestamp: '8h ago',
    postType: 'question',
    content: 'My sweet maize leaves are starting to show purple shading along the margins. Is this a phosphorus deficiency or cold injury? Any tips on what fertilizer to apply?',
    imageUrl: sweetMaizeImg,
    likesCount: 15,
    commentsCount: 5,
    hasLiked: false,
    comments: [
      {
        id: 'c_51',
        authorName: 'Dr. Ramesh G.',
        role: 'Expert',
        content: 'Typically, purple tinting in corn indicates Phosphorus deficiency, especially in early vegetative stages. Apply SSP (Single Super Phosphate) or DAP as a soil dressing.',
        timestamp: '6h ago'
      }
    ]
  },
  {
    id: 'post_6',
    authorName: 'Agro Weather Lab',
    avatarUrl: 'https://images.unsplash.com/photo-1534308983496-4fabb1a015ee?w=100&auto=format&fit=crop&q=80',
    role: 'Expert',
    isVerified: true,
    timestamp: '12h ago',
    postType: 'weather',
    content: 'HEAVY RAINFALL ALERT: Intense thunder activities and wind speeds exceeding 35 km/h predicted for Nashik and Wardha districts over the next 48 hours. Secure stored onion piles and delay pesticide sprays.',
    likesCount: 62,
    commentsCount: 9,
    hasLiked: false,
    comments: [
      {
        id: 'c_61',
        authorName: 'Kishor Bodke',
        role: 'Farmer',
        content: 'Thanks for the warning. Covering our tarpaulin shelters today.',
        timestamp: '10h ago'
      }
    ]
  },
  {
    id: 'post_7',
    authorName: 'Savita Salunkhe',
    avatarUrl: 'https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=100&auto=format&fit=crop&q=80',
    role: 'Farmer',
    isVerified: true,
    timestamp: '1d ago',
    postType: 'success',
    content: 'Proud to share that my organic farming trial of Bt Cotton yielded 12 quintals per acre this season! Minimizing chemical sprays and relying on bio-pesticides and farmyard manure saved ₹6,000/acre in input costs. Highly recommend moving towards semi-organic practices! 🌟🌾',
    likesCount: 88,
    commentsCount: 12,
    hasLiked: false,
    comments: [
      {
        id: 'c_71',
        authorName: 'Megha Patil',
        role: 'Farmer',
        content: 'Incredible success Savita! You are an inspiration for all of us women farmers.',
        timestamp: '20h ago'
      }
    ]
  }
];
