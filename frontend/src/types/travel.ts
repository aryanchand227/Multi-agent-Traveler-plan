/** Core travel planning types — mirrors backend schemas */
import type { TransportComparison } from "./transport";
import type { AccommodationOption } from "./accommodation";
import type { ActivityOption } from "./activity";
import type { WeatherForecast, BudgetBreakdown, Itinerary } from "./itinerary";

export type TravelStyle = "budget" | "standard" | "premium" | "luxury" | "custom";
export type OutputDetail = "brief" | "standard" | "detailed";
export type TravelRunStatus =
  | "pending"
  | "clarifying"
  | "planning"
  | "validating"
  | "completed"
  | "failed"
  | "cancelled";

export interface TravelPlanRequest {
  raw_request?: string;
  origin?: string;
  destination?: string;
  departure_date?: string;
  return_date?: string;
  travelers?: number;
  budget?: number;
  currency?: string;
  travel_style?: TravelStyle;
  preferred_transport?: string[];
  interests?: string[];
  accommodation_preference?: string;
  output_detail?: OutputDetail;
  additional_requirements?: string;
}

export interface ClarificationQuestion {
  field: string;
  question: string;
  required: boolean;
  options?: string[];
}

export interface TravelRunResponse {
  request_id: string;
  run_id: string;
  status: TravelRunStatus;
  started_at?: string;
  completed_at?: string;
  error?: string;
  clarification_questions?: ClarificationQuestion[];
  final_plan?: FinalTravelPlan;
}

export interface ReplanRequest {
  message: string;
  changes?: Record<string, unknown>;
}

export interface UserPreferences {
  user_id: string;
  preferred_transport?: string;
  travel_style?: string;
  budget_preference?: number;
  hotel_preference?: string;
  activity_preferences: string[];
  food_preferences: string[];
  default_currency: string;
  default_output_detail: string;
}

export interface UserPreferencesUpdate {
  preferred_transport?: string;
  travel_style?: string;
  budget_preference?: number;
  hotel_preference?: string;
  activity_preferences?: string[];
  food_preferences?: string[];
  default_currency?: string;
  default_output_detail?: string;
}

export interface DataSource {
  provider: string;
  source_type: "mock" | "live" | "cached" | string;
  retrieved_at?: string;
}

export interface ValidationResult {
  is_valid: boolean;
  errors: string[];
  warnings: string[];
  checks_passed: string[];
}

export interface TripSummary {
  request_id: string;
  origin: string;
  destination: string;
  departure_date?: string;
  return_date?: string;
  travelers: number;
  duration_days: number;
  budget?: number;
  currency: string;
  travel_style: string;
  interests: string[];
}

export interface FinalTravelPlan {
  trip_summary: TripSummary;
  transportation?: TransportComparison;
  accommodation?: AccommodationOption;
  accommodation_alternatives?: AccommodationOption[];
  activities?: ActivityOption[];
  weather?: WeatherForecast;
  budget?: BudgetBreakdown;
  itinerary?: Itinerary;
  decision_factors?: string[];
  warnings?: string[];
  data_sources?: DataSource[];
  validation?: ValidationResult;
  human_readable_summary?: string;
  generated_at?: string;
}
