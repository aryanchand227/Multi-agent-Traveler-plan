export type ActivityCategory =
  | "adventure"
  | "cultural"
  | "food"
  | "nightlife"
  | "nature"
  | "historical"
  | "shopping"
  | "relaxation"
  | "family"
  | "indoor"
  | "outdoor";

export interface ActivityOption {
  id: string;
  name: string;
  category: ActivityCategory;
  location?: string;
  description?: string;
  estimated_duration_minutes?: number;
  estimated_cost?: number;
  best_time?: string;
  weather_dependency?: boolean;
  source: string;
  source_type: "mock" | "live" | "cached";
  retrieved_at?: string;
}
