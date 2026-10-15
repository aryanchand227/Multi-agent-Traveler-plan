export type AgentEventType =
  | "started"
  | "completed"
  | "failed"
  | "retrying"
  | "tool_called"
  | "progress";

export interface AgentEvent {
  id?: string;
  run_id: string;
  agent_name: string;
  event_type: AgentEventType;
  message?: string;
  metadata?: Record<string, unknown>;
  duration_ms?: number;
  timestamp: string;
}

export interface AgentStatus {
  name: string;
  displayName: string;
  status: "pending" | "running" | "completed" | "failed";
  message?: string;
  startedAt?: string;
  completedAt?: string;
  durationMs?: number;
}

export const AGENT_DISPLAY_NAMES: Record<string, string> = {
  intake_agent: "Travel Requirements",
  clarification_agent: "Information Check",
  travel_manager: "Travel Manager",
  transport_supervisor: "Transport Search",
  bus_agent: "Bus Options",
  train_agent: "Train Options",
  flight_agent: "Flight Options",
  accommodation_agent: "Accommodation",
  destination_agent: "Activities & Attractions",
  weather_agent: "Weather Check",
  budget_agent: "Budget Analysis",
  itinerary_agent: "Itinerary Builder",
  validation_agent: "Plan Validation",
  final_planner: "Final Planning",
};
