/**
 * Server-Sent Events client for real-time agent progress.
 * Attaches auth token via query param and enables credentials.
 */

import { getAuthToken } from "./api";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface SSEEvent {
  type: string;
  agent: string;
  message: string;
  progress_pct?: number;
  details?: Record<string, unknown>;
}

export function connectToAgentEvents(
  requestId: string,
  onEvent: (event: SSEEvent) => void,
  onError?: (error: Event) => void
): EventSource {
  const token = getAuthToken();
  const tokenParam = token ? `?token=${encodeURIComponent(token)}` : "";
  const url = `${API_BASE}/api/v1/travel/${requestId}/events${tokenParam}`;

  const eventSource = new EventSource(url, { withCredentials: true });

  const parseAndCall = (dataStr: string) => {
    try {
      const parsed = JSON.parse(dataStr);
      onEvent(parsed);
    } catch (e) {
      console.error("Failed to parse SSE event data:", e);
    }
  };

  eventSource.addEventListener("agent_started", (e) => parseAndCall(e.data));
  eventSource.addEventListener("agent_completed", (e) => parseAndCall(e.data));
  eventSource.addEventListener("agent_failed", (e) => parseAndCall(e.data));
  eventSource.addEventListener("agent_progress", (e) => parseAndCall(e.data));
  eventSource.onmessage = (e) => parseAndCall(e.data);

  eventSource.addEventListener("planning_complete", (e) => {
    parseAndCall(e.data);
    eventSource.close();
  });

  eventSource.onerror = (e) => {
    onError?.(e);
  };

  return eventSource;
}
