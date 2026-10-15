/**
 * API client for communicating with the FastAPI backend.
 * All API calls go through this module — handles JWT tokens, error parsing, and credentials.
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export class ApiError extends Error {
  status: number;
  details?: Record<string, unknown>;

  constructor(message: string, status: number, details?: Record<string, unknown>) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.details = details;
  }
}

export function getAuthToken(): string | null {
  if (typeof window !== "undefined") {
    return localStorage.getItem("auth_token");
  }
  return null;
}

export function setAuthToken(token: string): void {
  if (typeof window !== "undefined") {
    localStorage.setItem("auth_token", token);
  }
}

export function clearAuthToken(): void {
  if (typeof window !== "undefined") {
    localStorage.removeItem("auth_token");
  }
}

async function request<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE}/api/v1${path}`;
  const token = getAuthToken();

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : { "X-User-ID": "default-user" }),
    ...((options.headers as Record<string, string>) || {}),
  };

  const response = await fetch(url, {
    credentials: "include",
    ...options,
    headers,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    let msg = error.message || error.detail;
    if (typeof msg === "object" && msg !== null) {
      msg = JSON.stringify(msg);
    }

    if (response.status === 429) {
      const retryAfter = response.headers.get("Retry-After");
      const retryMsg = retryAfter ? ` Please retry in ${retryAfter} seconds.` : "";
      msg = msg || `Rate limit exceeded.${retryMsg}`;
    }

    throw new ApiError(
      msg || `Request failed with status ${response.status}: ${response.statusText}`,
      response.status,
      error.details
    );
  }

  return response.json();
}

// --- Health & Readiness ---

export async function checkHealth() {
  return request<{
    status: string;
    app_name: string;
    version: string;
    environment: string;
    database: string;
    llm_provider: string;
    mock_providers: boolean;
    timestamp: string;
  }>("/health");
}

export async function checkReadiness() {
  return request<{
    status: string;
    database: string;
    environment: string;
    llm_configured: boolean;
    timestamp: string;
  }>("/ready");
}

// --- Authentication ---

export interface UserProfile {
  id: string;
  email: string;
  display_name?: string | null;
  is_active: boolean;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: UserProfile;
}

export async function registerUser(email: string, password: string, displayName?: string): Promise<AuthResponse> {
  const res = await request<AuthResponse>("/auth/register", {
    method: "POST",
    body: JSON.stringify({ email, password, display_name: displayName }),
  });
  setAuthToken(res.access_token);
  return res;
}

export async function loginUser(email: string, password: string): Promise<AuthResponse> {
  const res = await request<AuthResponse>("/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
  setAuthToken(res.access_token);
  return res;
}

export async function getCurrentUser(): Promise<UserProfile> {
  return request<UserProfile>("/auth/me");
}

export async function logoutUser(): Promise<{ message: string }> {
  clearAuthToken();
  return request<{ message: string }>("/auth/logout", { method: "POST" });
}

// --- Travel Planning ---

import type { TravelPlanRequest, TravelRunResponse, ReplanRequest } from "@/types/travel";

export async function createTravelPlan(
  data: TravelPlanRequest
): Promise<TravelRunResponse> {
  return request<TravelRunResponse>("/travel/plan", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function submitClarification(
  requestId: string,
  responses: Record<string, string>
): Promise<TravelRunResponse> {
  return request<TravelRunResponse>("/travel/clarify", {
    method: "POST",
    body: JSON.stringify({ request_id: requestId, responses }),
  });
}

export async function getTravelPlan(
  requestId: string
): Promise<TravelRunResponse> {
  return request<TravelRunResponse>(`/travel/${requestId}`);
}

export async function replanTravel(
  requestId: string,
  data: ReplanRequest
): Promise<TravelRunResponse> {
  return request<TravelRunResponse>(`/travel/${requestId}/replan`, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function getTravelHistory(): Promise<Array<{
  request_id: string;
  origin?: string;
  destination?: string;
  departure_date?: string;
  travelers?: number;
  budget?: number;
  currency?: string;
  status: string;
  created_at?: string;
}>> {
  return request("/travel/history");
}

// --- Preferences ---

import type { UserPreferences, UserPreferencesUpdate } from "@/types/travel";

export async function getPreferences(): Promise<UserPreferences> {
  return request<UserPreferences>("/preferences");
}

export async function updatePreferences(
  data: UserPreferencesUpdate
): Promise<UserPreferences> {
  return request<UserPreferences>("/preferences", {
    method: "PUT",
    body: JSON.stringify(data),
  });
}
