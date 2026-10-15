"use client";

import React, { useEffect, useState } from "react";
import { connectToAgentEvents, type SSEEvent } from "@/lib/sse";

interface AgentProgressProps {
  requestId: string;
  onComplete: () => void;
}

export default function AgentProgress({ requestId, onComplete }: AgentProgressProps) {
  const [events, setEvents] = useState<SSEEvent[]>([]);
  const [currentAgent, setCurrentAgent] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const eventSource = connectToAgentEvents(
      requestId,
      (event) => {
        setEvents((prev) => [...prev, event]);
        
        if (event.type === "agent_started") {
          setCurrentAgent(event.agent);
        } else if (event.type === "agent_completed" || event.type === "agent_failed") {
          setCurrentAgent(null);
        } else if (event.type === "planning_complete") {
          onComplete();
        }
      },
      (err) => {
        console.error("SSE Error:", err);
        setError("Lost connection to progress updates. The plan might still be generating.");
      }
    );

    return () => {
      eventSource.close();
    };
  }, [requestId, onComplete]);

  return (
    <div className="bg-white rounded-lg shadow p-6 max-w-2xl mx-auto mt-8">
      <h2 className="text-xl font-bold mb-4 text-gray-900">Planning Your Trip...</h2>
      
      <div className="space-y-4">
        {events.map((ev, idx) => (
          <div key={idx} className="flex items-start gap-3">
            <div className="mt-1 flex-shrink-0">
              {ev.type === "agent_completed" ? (
                <div className="h-4 w-4 rounded-full bg-green-500" />
              ) : ev.type === "agent_failed" ? (
                <div className="h-4 w-4 rounded-full bg-red-500" />
              ) : ev.type === "planning_complete" ? (
                <div className="h-4 w-4 rounded-full bg-blue-500" />
              ) : (
                <div className="h-4 w-4 rounded-full bg-gray-300" />
              )}
            </div>
            <div>
              <p className="text-sm font-medium text-gray-900">{ev.agent} <span className="text-gray-500 font-normal ml-2">{ev.type}</span></p>
              <p className="text-sm text-gray-600">{ev.message}</p>
            </div>
          </div>
        ))}

        {currentAgent && (
          <div className="flex items-center gap-3 pt-2">
            <div className="flex space-x-1">
              <div className="h-2 w-2 bg-blue-600 rounded-full animate-bounce [animation-delay:-0.3s]"></div>
              <div className="h-2 w-2 bg-blue-600 rounded-full animate-bounce [animation-delay:-0.15s]"></div>
              <div className="h-2 w-2 bg-blue-600 rounded-full animate-bounce"></div>
            </div>
            <span className="text-sm text-blue-600 font-medium">
              {currentAgent} is working...
            </span>
          </div>
        )}

        {error && (
          <p className="text-sm text-yellow-600 bg-yellow-50 p-2 rounded mt-4">
            {error}
          </p>
        )}
      </div>
    </div>
  );
}
