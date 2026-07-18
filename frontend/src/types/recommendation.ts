export type RecommendationRequest = {
  age_range: string;
  skin_type: string;
  experience_level: string;
  coverage: string;
  max_price: number;
  skin_tone: string;
  skin_concerns: string[];
};

export type ProductRecommendation = {
  category: string;
  product_name: string;
  brand: string;
  price: number;
  url: string;
  image_link?: string;
  match_score: number;
  ml_score?: number | null;
  routine_step?: string;
  reason: string;
};

export type RecommendationResponse = {
  profile: RecommendationRequest;
  recommendations: ProductRecommendation[];
};

export type FormOptions = {
  age_ranges: string[];
  skin_types: string[];
  experience_levels: string[];
  coverage_preferences: string[];
  skin_tones: string[];
  skin_concerns: string[];
};