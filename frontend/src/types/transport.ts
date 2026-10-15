export type TransportMode = "bus" | "train" | "flight";
export type ProviderType = "government" | "private" | "airline";
export type ComfortLevel = "economy" | "standard" | "premium" | "luxury";
export type SourceType = "mock" | "live" | "cached";

export interface TransportOption {
  id: string;
  mode: TransportMode;
  provider: string;
  provider_type: ProviderType;
  origin: string;
  destination: string;
  departure_time?: string;
  arrival_time?: string;
  duration_minutes?: number;
  price_per_person: number;
  total_price: number;
  stops: number;
  comfort_level: ComfortLevel;
  vehicle_info?: string;
  availability: string;
  source: string;
  source_type: SourceType;
  retrieved_at: string;
  score?: number;
  decision_factors?: Record<string, unknown> | string[];
}

export interface TransportComparison {
  selected: TransportOption;
  alternatives: TransportOption[];
  cheapest?: TransportOption;
  fastest?: TransportOption;
  recommended?: TransportOption;
  recommendation_reason?: string;
}
