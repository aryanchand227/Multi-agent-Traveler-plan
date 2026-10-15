import { useState, useCallback, useEffect } from "react";
import {
  createTravelPlan,
  getTravelPlan,
  submitClarification,
  replanTravel,
} from "@/lib/api";
import type {
  TravelPlanRequest,
  TravelRunResponse,
  ReplanRequest,
} from "@/types/travel";

export function useTravelPlan(initialRequestId?: string) {
  const [requestId, setRequestId] = useState<string | undefined>(initialRequestId);
  const [data, setData] = useState<TravelRunResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const fetchPlan = useCallback(async (id: string) => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await getTravelPlan(id);
      setData(res);
      return res;
    } catch (err: any) {
      const msg = err.message || "Failed to load travel plan";
      setError(msg);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    if (initialRequestId) {
      setRequestId(initialRequestId);
      fetchPlan(initialRequestId).catch(() => {});
    }
  }, [initialRequestId, fetchPlan]);

  const startPlan = useCallback(async (req: TravelPlanRequest) => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await createTravelPlan(req);
      setRequestId(res.request_id);
      setData(res);
      return res;
    } catch (err: any) {
      const msg = err.message || "Failed to start travel plan";
      setError(msg);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const clarify = useCallback(
    async (responses: Record<string, string>) => {
      if (!requestId) {
        throw new Error("No active request ID to clarify");
      }
      setIsLoading(true);
      setError(null);
      try {
        const res = await submitClarification(requestId, responses);
        setData(res);
        return res;
      } catch (err: any) {
        const msg = err.message || "Failed to submit clarifications";
        setError(msg);
        throw err;
      } finally {
        setIsLoading(false);
      }
    },
    [requestId]
  );

  const requestReplan = useCallback(
    async (replanReq: ReplanRequest) => {
      if (!requestId) {
        throw new Error("No active request ID to replan");
      }
      setIsLoading(true);
      setError(null);
      try {
        const res = await replanTravel(requestId, replanReq);
        setData(res);
        return res;
      } catch (err: any) {
        const msg = err.message || "Failed to request replan";
        setError(msg);
        throw err;
      } finally {
        setIsLoading(false);
      }
    },
    [requestId]
  );

  const refresh = useCallback(() => {
    if (requestId) {
      return fetchPlan(requestId);
    }
    return Promise.resolve(null);
  }, [requestId, fetchPlan]);

  return {
    requestId,
    data,
    plan: data?.final_plan,
    status: data?.status,
    isLoading,
    error,
    startPlan,
    clarify,
    replan: requestReplan,
    refresh,
  };
}
