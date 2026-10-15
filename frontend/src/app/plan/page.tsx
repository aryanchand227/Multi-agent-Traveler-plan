"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import PlanForm from "@/components/PlanForm";
import ClarificationDialog from "@/components/ClarificationDialog";
import { createTravelPlan, submitClarification } from "@/lib/api";
import type { TravelPlanRequest, TravelRunResponse, ClarificationQuestion } from "@/types/travel";

export default function PlanPage() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const [clarificationQuestions, setClarificationQuestions] = useState<ClarificationQuestion[] | null>(null);
  const [requestId, setRequestId] = useState<string | null>(null);

  const handlePlanSubmit = async (data: TravelPlanRequest) => {
    setIsLoading(true);
    setError(null);
    try {
      const response: TravelRunResponse = await createTravelPlan(data);
      handleResponse(response);
    } catch (err: any) {
      setError(err.message || "An error occurred");
    } finally {
      setIsLoading(false);
    }
  };

  const handleClarificationSubmit = async (responses: Record<string, string>) => {
    if (!requestId) return;
    
    setIsLoading(true);
    setError(null);
    try {
      const response: TravelRunResponse = await submitClarification(requestId, responses);
      handleResponse(response);
    } catch (err: any) {
      setError(err.message || "An error occurred");
    } finally {
      setIsLoading(false);
    }
  };

  const handleResponse = (response: TravelRunResponse) => {
    if (response.status === "clarifying" && response.clarification_questions) {
      setRequestId(response.request_id);
      setClarificationQuestions(response.clarification_questions);
    } else {
      // Redirect to results page for tracking progress or viewing final plan
      router.push(`/results/${response.request_id}`);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-3xl mx-auto">
        <h1 className="text-3xl font-extrabold text-center text-gray-900 mb-8">
          AI Travel Planner
        </h1>
        
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-6">
            {error}
          </div>
        )}

        <PlanForm onSubmit={handlePlanSubmit} isLoading={isLoading && !clarificationQuestions} />

        {clarificationQuestions && (
          <ClarificationDialog
            questions={clarificationQuestions}
            onSubmit={handleClarificationSubmit}
            isLoading={isLoading}
          />
        )}
      </div>
    </div>
  );
}
