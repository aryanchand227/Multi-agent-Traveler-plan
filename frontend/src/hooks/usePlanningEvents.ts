import { useState, useEffect, useCallback } from "react";
import { connectToAgentEvents, type SSEEvent } from "@/lib/sse";
import { AGENT_DISPLAY_NAMES, type AgentStatus } from "@/types/agent";

export function usePlanningEvents(requestId?: string, onComplete?: () => void) {
  const [events, setEvents] = useState<SSEEvent[]>([]);
  const [currentAgent, setCurrentAgent] = useState<string | null>(null);
  const [isFinished, setIsFinished] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!requestId) return;

    setEvents([]);
    setCurrentAgent(null);
    setIsFinished(false);
    setError(null);

    const eventSource = connectToAgentEvents(
      requestId,
      (event: SSEEvent) => {
        setEvents((prev) => [...prev, event]);

        if (event.type === "agent_started") {
          setCurrentAgent(event.agent);
        } else if (
          event.type === "agent_completed" ||
          event.type === "agent_failed"
        ) {
          setCurrentAgent(null);
        } else if (event.type === "planning_complete") {
          setIsFinished(true);
          setCurrentAgent(null);
          onComplete?.();
        }
      },
      (err) => {
        console.warn("SSE connection status:", err);
      }
    );

    return () => {
      eventSource.close();
    };
  }, [requestId, onComplete]);

  // Derive agent status summary
  const agentStatuses: Record<string, AgentStatus> = {};
  for (const ev of events) {
    const key = ev.agent;
    const displayName = AGENT_DISPLAY_NAMES[key] || key;
    if (ev.type === "agent_started") {
      agentStatuses[key] = {
        name: key,
        displayName,
        status: "running",
        message: ev.message,
      };
    } else if (ev.type === "agent_completed") {
      agentStatuses[key] = {
        name: key,
        displayName,
        status: "completed",
        message: ev.message,
      };
    } else if (ev.type === "agent_failed") {
      agentStatuses[key] = {
        name: key,
        displayName,
        status: "failed",
        message: ev.message,
      };
    }
  }

  const clearEvents = useCallback(() => {
    setEvents([]);
    setCurrentAgent(null);
    setIsFinished(false);
  }, []);

  return {
    events,
    currentAgent,
    isFinished,
    error,
    agentStatuses,
    clearEvents,
  };
}
