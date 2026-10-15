"use client";

import React, { useEffect, useState, use } from "react";
import { getTravelPlan } from "@/lib/api";
import AgentProgress from "@/components/AgentProgress";
import ResultsDashboard from "@/components/ResultsDashboard";
import type { TravelRunResponse } from "@/types/travel";

export default function ResultsPage({ params }: { params: Promise<{ requestId: string }> }) {
  // React 19 unwrapping of params
  const { requestId } = use(params);
  
  const [data, setData] = useState<TravelRunResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchPlan = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await getTravelPlan(requestId);
      setData(response);
    } catch (err: any) {
      setError(err.message || "Failed to fetch travel plan");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchPlan();
  }, [requestId]);

  const handlePlanningComplete = () => {
    // Small delay to ensure backend has saved the final plan
    setTimeout(() => {
      fetchPlan();
    }, 1000);
  };

  if (isLoading && !data) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 py-12 px-4">
        <div className="max-w-3xl mx-auto bg-red-50 p-6 rounded-lg shadow border border-red-200">
          <h2 className="text-xl font-bold text-red-800 mb-2">Error</h2>
          <p className="text-red-700">{error}</p>
          <button 
            onClick={fetchPlan}
            className="mt-4 bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (!data) return null;

  const isPlanning = data.status === "pending" || data.status === "planning" || data.status === "validating";

  return (
    <div className="min-h-screen bg-gray-50">
      {isPlanning ? (
        <div className="py-12 px-4">
          <AgentProgress requestId={requestId} onComplete={handlePlanningComplete} />
        </div>
      ) : data.status === "failed" ? (
        <div className="py-12 px-4 text-center max-w-2xl mx-auto">
          <h2 className="text-2xl font-bold text-red-600 mb-2">Planning Failed</h2>
          <div className="bg-red-50 p-4 rounded-lg border border-red-200 text-left">
            <p className="text-red-800 font-semibold mb-1">Error from AI Agent:</p>
            <p className="text-red-700 break-words">{data.error || "Unknown error occurred."}</p>
          </div>
        </div>
      ) : data.status === "completed" && data.final_plan ? (
        <ResultsDashboard
          plan={data.final_plan}
          requestId={requestId}
          onReplanComplete={fetchPlan}
        />
      ) : (
        <div className="py-12 px-4 text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Unexpected Status: {data.status}</h2>
          <p className="text-gray-600">We couldn't display the plan correctly.</p>
        </div>
      )}
    </div>
  );
}
