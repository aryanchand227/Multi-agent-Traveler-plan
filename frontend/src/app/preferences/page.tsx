"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/context/AuthContext";
import { usePreferences } from "@/hooks/usePreferences";
import type { UserPreferencesUpdate } from "@/types/travel";

const ACTIVITY_OPTIONS = [
  "Adventure",
  "Cultural",
  "Food & Dining",
  "Nightlife",
  "Nature",
  "Historical",
  "Shopping",
  "Relaxation",
  "Family-friendly",
  "Photography",
];

const FOOD_OPTIONS = [
  "Vegetarian",
  "Vegan",
  "Halal",
  "Kosher",
  "Gluten-free",
  "Local Street Food",
  "Fine Dining",
  "Seafood",
];

export default function PreferencesPage() {
  const router = useRouter();
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const { preferences, isLoading, isSaving, error, saveSuccess, savePreferences } =
    usePreferences();

  const [preferredTransport, setPreferredTransport] = useState<string>("flight");
  const [travelStyle, setTravelStyle] = useState<string>("standard");
  const [budgetPreference, setBudgetPreference] = useState<number | undefined>(undefined);
  const [hotelPreference, setHotelPreference] = useState<string>("hotel_3star");
  const [selectedActivities, setSelectedActivities] = useState<string[]>([]);
  const [selectedFood, setSelectedFood] = useState<string[]>([]);
  const [defaultCurrency, setDefaultCurrency] = useState<string>("INR");
  const [defaultOutputDetail, setDefaultOutputDetail] = useState<string>("standard");

  useEffect(() => {
    if (preferences) {
      if (preferences.preferred_transport) setPreferredTransport(preferences.preferred_transport);
      if (preferences.travel_style) setTravelStyle(preferences.travel_style);
      if (preferences.budget_preference) setBudgetPreference(preferences.budget_preference);
      if (preferences.hotel_preference) setHotelPreference(preferences.hotel_preference);
      if (preferences.activity_preferences) setSelectedActivities(preferences.activity_preferences);
      if (preferences.food_preferences) setSelectedFood(preferences.food_preferences);
      if (preferences.default_currency) setDefaultCurrency(preferences.default_currency);
      if (preferences.default_output_detail) setDefaultOutputDetail(preferences.default_output_detail);
    }
  }, [preferences]);

  const toggleActivity = (act: string) => {
    setSelectedActivities((prev) =>
      prev.includes(act) ? prev.filter((a) => a !== act) : [...prev, act]
    );
  };

  const toggleFood = (food: string) => {
    setSelectedFood((prev) =>
      prev.includes(food) ? prev.filter((f) => f !== food) : [...prev, food]
    );
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!isAuthenticated) {
      router.push("/login?redirect=/preferences");
      return;
    }

    const updatePayload: UserPreferencesUpdate = {
      preferred_transport: preferredTransport,
      travel_style: travelStyle,
      budget_preference: budgetPreference,
      hotel_preference: hotelPreference,
      activity_preferences: selectedActivities,
      food_preferences: selectedFood,
      default_currency: defaultCurrency,
      default_output_detail: defaultOutputDetail,
    };

    try {
      await savePreferences(updatePayload);
    } catch (err: any) {
      if (err?.status === 401) {
        router.push("/login?redirect=/preferences");
      }
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-3xl mx-auto">
        <div className="mb-8 text-center">
          <h1 className="text-3xl font-extrabold text-gray-900">Travel Preferences</h1>
          <p className="text-sm text-gray-600 mt-2">
            Customize your persistent travel profile. The AI Travel Manager recalls these preferences during planning.
          </p>
        </div>

        {!authLoading && !isAuthenticated && (
          <div className="mb-6 p-4 bg-blue-50 border border-blue-200 text-blue-900 rounded-xl flex flex-col sm:flex-row sm:items-center justify-between gap-3 shadow-sm">
            <div className="flex items-start sm:items-center gap-3">
              <span className="text-2xl">ℹ️</span>
              <div>
                <p className="font-semibold text-sm">Guest Mode — Showing Default Preferences</p>
                <p className="text-xs text-blue-700">
                  Sign in to customize and save your preferences for future AI travel plans.
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2 self-end sm:self-auto flex-shrink-0">
              <Link
                href="/login?redirect=/preferences"
                className="px-3.5 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-700 text-white font-medium text-xs shadow-sm transition-colors"
              >
                Sign In to Save
              </Link>
            </div>
          </div>
        )}

        {saveSuccess && (
          <div className="mb-6 p-4 bg-emerald-50 border border-emerald-200 text-emerald-800 rounded-lg text-sm font-medium flex items-center gap-2">
            <span>✓</span> Preferences saved successfully! Future plans will automatically adapt to your tastes.
          </div>
        )}

        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 text-red-700 rounded-lg text-sm">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 sm:p-8 space-y-6">
          {/* Preferred Transport */}
          <div>
            <label className="block text-sm font-semibold text-gray-900 mb-2">
              Preferred Transportation Mode
            </label>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              {[
                { id: "flight", label: "✈ Flight", desc: "Fastest" },
                { id: "train", label: "🚆 Train", desc: "Scenic & balanced" },
                { id: "bus", label: "🚌 Bus", desc: "Economical" },
                { id: "any", label: "🔄 Any Mode", desc: "Best value" },
              ].map((m) => (
                <button
                  type="button"
                  key={m.id}
                  onClick={() => setPreferredTransport(m.id)}
                  className={`p-3 rounded-lg border text-left transition ${
                    preferredTransport === m.id
                      ? "border-blue-600 bg-blue-50/70 text-blue-950 font-bold ring-1 ring-blue-600"
                      : "border-gray-200 bg-white hover:bg-gray-50 text-gray-700"
                  }`}
                >
                  <p className="text-sm">{m.label}</p>
                  <p className="text-xs text-gray-500 font-normal mt-0.5">{m.desc}</p>
                </button>
              ))}
            </div>
          </div>

          {/* Travel Style */}
          <div>
            <label className="block text-sm font-semibold text-gray-900 mb-2">
              Default Travel Style
            </label>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              {["budget", "standard", "premium", "luxury"].map((style) => (
                <button
                  type="button"
                  key={style}
                  onClick={() => setTravelStyle(style)}
                  className={`p-3 rounded-lg border text-center capitalize transition ${
                    travelStyle === style
                      ? "border-blue-600 bg-blue-50/70 text-blue-950 font-bold ring-1 ring-blue-600"
                      : "border-gray-200 bg-white hover:bg-gray-50 text-gray-700"
                  }`}
                >
                  <span className="text-sm">{style}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Hotel Preference */}
          <div>
            <label className="block text-sm font-semibold text-gray-900 mb-2">
              Preferred Accommodation Type
            </label>
            <select
              value={hotelPreference}
              onChange={(e) => setHotelPreference(e.target.value)}
              className="w-full px-4 py-2.5 rounded-lg border border-gray-300 bg-white text-gray-900 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="hostel">Hostel / Backpacker</option>
              <option value="budget_hotel">Budget Hotel / Guesthouse</option>
              <option value="hotel_3star">3-Star Hotel (Balanced)</option>
              <option value="hotel_4star">4-Star Hotel / Boutique</option>
              <option value="hotel_5star">5-Star Luxury Hotel</option>
              <option value="resort">Resort & Spa</option>
            </select>
          </div>

          {/* Activities Multi-select */}
          <div>
            <label className="block text-sm font-semibold text-gray-900 mb-2">
              Favorite Travel Interests & Activities
            </label>
            <div className="flex flex-wrap gap-2">
              {ACTIVITY_OPTIONS.map((act) => {
                const isSelected = selectedActivities.includes(act);
                return (
                  <button
                    type="button"
                    key={act}
                    onClick={() => toggleActivity(act)}
                    className={`px-3 py-1.5 rounded-full text-xs font-medium border transition ${
                      isSelected
                        ? "bg-purple-600 text-white border-purple-600 shadow-sm"
                        : "bg-white text-gray-700 border-gray-300 hover:border-gray-400"
                    }`}
                  >
                    {isSelected ? `✓ ${act}` : `+ ${act}`}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Food Preferences Multi-select */}
          <div>
            <label className="block text-sm font-semibold text-gray-900 mb-2">
              Dietary & Food Preferences
            </label>
            <div className="flex flex-wrap gap-2">
              {FOOD_OPTIONS.map((food) => {
                const isSelected = selectedFood.includes(food);
                return (
                  <button
                    type="button"
                    key={food}
                    onClick={() => toggleFood(food)}
                    className={`px-3 py-1.5 rounded-full text-xs font-medium border transition ${
                      isSelected
                        ? "bg-emerald-600 text-white border-emerald-600 shadow-sm"
                        : "bg-white text-gray-700 border-gray-300 hover:border-gray-400"
                    }`}
                  >
                    {isSelected ? `✓ ${food}` : `+ ${food}`}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Currency and Output Detail Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2">
            <div>
              <label className="block text-sm font-semibold text-gray-900 mb-1">
                Default Currency
              </label>
              <select
                value={defaultCurrency}
                onChange={(e) => setDefaultCurrency(e.target.value)}
                className="w-full px-3 py-2 rounded-lg border border-gray-300 bg-white text-gray-900 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="INR">INR (₹)</option>
                <option value="USD">USD ($)</option>
                <option value="EUR">EUR (€)</option>
                <option value="GBP">GBP (£)</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-semibold text-gray-900 mb-1">
                Output Detail Level
              </label>
              <select
                value={defaultOutputDetail}
                onChange={(e) => setDefaultOutputDetail(e.target.value)}
                className="w-full px-3 py-2 rounded-lg border border-gray-300 bg-white text-gray-900 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="brief">Brief (High-level summary)</option>
                <option value="standard">Standard (Recommended)</option>
                <option value="detailed">Detailed (Exhaustive breakdown)</option>
              </select>
            </div>
          </div>

          {/* Save Button */}
          <div className="pt-4 border-t border-gray-100 flex justify-end">
            <button
              type="submit"
              disabled={isSaving}
              className="bg-blue-600 hover:bg-blue-700 text-white font-medium px-6 py-2.5 rounded-lg text-sm shadow-sm transition disabled:opacity-50 flex items-center gap-2"
            >
              {isSaving ? (
                <>
                  <div className="h-4 w-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  <span>Saving Preferences...</span>
                </>
              ) : (
                <span>Save Preferences</span>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
