"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import PlanForm from "@/components/PlanForm";
import ClarificationDialog from "@/components/ClarificationDialog";
import { createTravelPlan, submitClarification } from "@/lib/api";
import { useAuth } from "@/context/AuthContext";
import type { TravelPlanRequest, TravelRunResponse, ClarificationQuestion } from "@/types/travel";

export default function PlanPage() {
  const router = useRouter();
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const [clarificationQuestions, setClarificationQuestions] = useState<ClarificationQuestion[] | null>(null);
  const [requestId, setRequestId] = useState<string | null>(null);

  const handlePlanSubmit = async (data: TravelPlanRequest) => {
    if (!isAuthenticated) {
      setError("Please sign in to generate and save your AI travel plan.");
      router.push("/login?redirect=/plan");
      return;
    }

    setIsLoading(true);
    setError(null);
    try {
      const response: TravelRunResponse = await createTravelPlan(data);
      handleResponse(response);
    } catch (err: any) {
      if (err?.status === 401) {
        setError("Your session has expired. Please sign in again to continue.");
        router.push("/login?redirect=/plan");
      } else {
        setError(err.message || "An error occurred while generating the plan.");
      }
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
      if (err?.status === 401) {
        setError("Your session has expired. Please sign in again to continue.");
        router.push("/login?redirect=/plan");
      } else {
        setError(err.message || "An error occurred while submitting clarification.");
      }
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

        {!authLoading && !isAuthenticated && (
          <div className="mb-6 p-4 rounded-xl border border-amber-200 bg-amber-50 text-amber-900 flex flex-col sm:flex-row sm:items-center justify-between gap-3 shadow-sm">
            <div className="flex items-start sm:items-center gap-3">
              <span className="text-2xl">🔐</span>
              <div>
                <p className="font-semibold text-sm">Account Required to Plan</p>
                <p className="text-xs text-amber-700">
                  Sign in or create a free account so the AI agent team can generate and store your custom itinerary.
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2 self-end sm:self-auto flex-shrink-0">
              <Link
                href="/login?redirect=/plan"
                className="px-3.5 py-1.5 rounded-lg bg-amber-600 hover:bg-amber-700 text-white font-medium text-xs shadow-sm transition-colors"
              >
                Sign In
              </Link>
              <Link
                href="/register?redirect=/plan"
                className="px-3.5 py-1.5 rounded-lg border border-amber-300 bg-white hover:bg-amber-100 text-amber-900 font-medium text-xs transition-colors"
              >
                Sign Up
              </Link>
            </div>
          </div>
        )}
        
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
