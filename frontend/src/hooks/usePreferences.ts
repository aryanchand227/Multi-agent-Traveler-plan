import { useState, useEffect, useCallback } from "react";
import { getPreferences, updatePreferences } from "@/lib/api";
import type { UserPreferences, UserPreferencesUpdate } from "@/types/travel";

export function usePreferences() {
  const [preferences, setPreferences] = useState<UserPreferences | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isSaving, setIsSaving] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [saveSuccess, setSaveSuccess] = useState<boolean>(false);

  const fetchPrefs = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const prefs = await getPreferences();
      setPreferences(prefs);
      return prefs;
    } catch (err: any) {
      setError(err.message || "Failed to load preferences");
      return null;
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchPrefs();
  }, [fetchPrefs]);

  const savePreferences = useCallback(
    async (updates: UserPreferencesUpdate) => {
      setIsSaving(true);
      setError(null);
      setSaveSuccess(false);
      try {
        const saved = await updatePreferences(updates);
        setPreferences(saved);
        setSaveSuccess(true);
        setTimeout(() => setSaveSuccess(false), 3000);
        return saved;
      } catch (err: any) {
        setError(err.message || "Failed to save preferences");
        throw err;
      } finally {
        setIsSaving(false);
      }
    },
    []
  );

  return {
    preferences,
    isLoading,
    isSaving,
    error,
    saveSuccess,
    savePreferences,
    refetch: fetchPrefs,
  };
}
