export type ItineraryItemType =
  | "transport"
  | "accommodation"
  | "activity"
  | "meal"
  | "rest"
  | "free_time";

export interface ItineraryItem {
  time_start?: string;
  time_end?: string;
  title: string;
  description?: string;
  item_type: ItineraryItemType;
  estimated_cost?: number;
  location?: string;
  notes?: string;
}

export interface ItineraryDay {
  day_number: number;
  date?: string;
  theme?: string;
  items: ItineraryItem[];
  notes?: string;
}

export interface Itinerary {
  title?: string;
  summary?: string;
  total_days: number;
  days: ItineraryDay[];
}

export interface BudgetBreakdown {
  transportation: number;
  accommodation: number;
  food: number;
  activities: number;
  local_transport: number;
  miscellaneous: number;
  total: number;
  budget?: number;
  remaining?: number;
  currency: string;
  status: "within_budget" | "near_budget" | "over_budget";
  per_person_total: number;
  optimization_suggestions: string[];
  warnings: string[];
}

export interface WeatherDay {
  date: string;
  temperature_high?: number;
  temperature_low?: number;
  condition?: string;
  precipitation_probability?: number;
  recommendation?: string;
}

export interface WeatherForecast {
  destination: string;
  days: WeatherDay[];
  source: string;
  source_type: "mock" | "live" | "cached";
  overall_recommendation?: string;
}
