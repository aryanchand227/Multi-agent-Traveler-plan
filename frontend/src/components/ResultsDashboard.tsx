"use client";

import React, { useState } from "react";
import type { FinalTravelPlan } from "@/types/travel";
import type { TransportOption } from "@/types/transport";
import type { AccommodationOption } from "@/types/accommodation";
import { replanTravel } from "@/lib/api";

interface ResultsDashboardProps {
  plan: FinalTravelPlan;
  requestId?: string;
  onReplanComplete?: () => void;
}

export default function ResultsDashboard({
  plan,
  requestId,
  onReplanComplete,
}: ResultsDashboardProps) {
  const {
    trip_summary,
    transportation,
    accommodation,
    accommodation_alternatives,
    activities,
    weather,
    budget,
    itinerary,
    validation,
    human_readable_summary,
    data_sources,
  } = plan;

  // Replan state
  const [replanMessage, setReplanMessage] = useState("");
  const [isReplanning, setIsReplanning] = useState(false);
  const [replanError, setReplanError] = useState<string | null>(null);
  const [replanSuccess, setReplanSuccess] = useState<string | null>(null);

  const handleReplanSubmit = async (customMsg?: string) => {
    const msg = customMsg || replanMessage;
    if (!msg.trim()) return;
    if (!requestId && !trip_summary?.request_id) {
      setReplanError("No request ID available for replanning.");
      return;
    }

    const id = requestId || trip_summary.request_id;
    setIsReplanning(true);
    setReplanError(null);
    setReplanSuccess(null);

    try {
      await replanTravel(id, { message: msg });
      setReplanSuccess("Replanning initiated! Refreshing your plan...");
      setReplanMessage("");
      if (onReplanComplete) {
        setTimeout(() => onReplanComplete(), 1500);
      } else {
        setTimeout(() => window.location.reload(), 1500);
      }
    } catch (err: any) {
      setReplanError(err.message || "Failed to replan trip.");
    } finally {
      setIsReplanning(false);
    }
  };

  const formatDecisionFactors = (factors?: Record<string, unknown> | string[] | any) => {
    if (!factors) return null;
    if (Array.isArray(factors)) {
      return factors.map((f, i) => (
        <span
          key={i}
          className="inline-block bg-slate-100 text-slate-700 text-xs px-2 py-0.5 rounded font-mono mr-1.5 mb-1"
        >
          {String(f)}
        </span>
      ));
    }
    if (typeof factors === "object") {
      return Object.entries(factors).map(([key, val]) => (
        <span
          key={key}
          className="inline-block bg-slate-100 text-slate-700 text-xs px-2 py-0.5 rounded font-mono mr-1.5 mb-1"
        >
          {key.replace(/_/g, " ")}:{" "}
          <span className="font-semibold">
            {typeof val === "number" ? val.toFixed(2) : String(val)}
          </span>
        </span>
      ));
    }
    return null;
  };

  const renderSourceBadge = (sourceType?: string) => {
    const isMock = sourceType === "mock";
    return (
      <span
        className={`text-[10px] uppercase font-bold tracking-wider px-1.5 py-0.5 rounded ${
          isMock
            ? "bg-amber-100 text-amber-800 border border-amber-300"
            : "bg-emerald-100 text-emerald-800 border border-emerald-300"
        }`}
      >
        {isMock ? "Mock Data" : "Live Source"}
      </span>
    );
  };

  return (
    <div className="space-y-8 max-w-6xl mx-auto py-8 px-4 text-gray-900">
      {/* Replan Notification */}
      {replanSuccess && (
        <div className="bg-green-50 border border-green-200 text-green-800 px-4 py-3 rounded-lg shadow-sm">
          {replanSuccess}
        </div>
      )}
      {replanError && (
        <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-lg shadow-sm">
          {replanError}
        </div>
      )}

      {/* Header & Overview Card */}
      <div className="bg-white p-6 sm:p-8 rounded-xl shadow-sm border border-gray-100">
        <div className="flex flex-wrap items-center justify-between gap-4 mb-3">
          <div>
            <span className="text-xs font-semibold tracking-wider text-blue-600 uppercase">
              Trip Plan
            </span>
            <h1 className="text-3xl sm:text-4xl font-extrabold text-gray-900 mt-1">
              {trip_summary?.origin} → {trip_summary?.destination}
            </h1>
          </div>
          <div className="flex items-center gap-2">
            <span className="bg-blue-100 text-blue-800 text-xs font-semibold px-3 py-1 rounded-full uppercase">
              {trip_summary?.travel_style || "Standard"} Style
            </span>
            {validation && (
              <span
                className={`text-xs font-semibold px-3 py-1 rounded-full ${
                  validation.is_valid
                    ? "bg-emerald-100 text-emerald-800"
                    : "bg-amber-100 text-amber-800"
                }`}
              >
                {validation.is_valid ? "✓ Validated Plan" : "⚠ Review Warnings"}
              </span>
            )}
          </div>
        </div>

        {human_readable_summary && (
          <p className="text-gray-700 leading-relaxed text-base mb-6 border-l-4 border-blue-500 pl-4 py-1 bg-blue-50/40 rounded-r">
            {human_readable_summary}
          </p>
        )}

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4">
          <div className="bg-slate-50 p-4 rounded-lg border border-slate-100">
            <p className="text-xs text-slate-500 font-medium uppercase">Dates & Duration</p>
            <p className="font-bold text-gray-900 mt-1">
              {trip_summary?.departure_date || "TBD"} - {trip_summary?.return_date || "TBD"}
            </p>
            <p className="text-xs text-slate-500 mt-0.5">
              {trip_summary?.duration_days} Days Trip
            </p>
          </div>
          <div className="bg-slate-50 p-4 rounded-lg border border-slate-100">
            <p className="text-xs text-slate-500 font-medium uppercase">Travelers</p>
            <p className="font-bold text-gray-900 mt-1">
              {trip_summary?.travelers} {trip_summary?.travelers === 1 ? "Person" : "People"}
            </p>
            <p className="text-xs text-slate-500 mt-0.5 capitalize">
              {trip_summary?.travel_style} Tier
            </p>
          </div>
          <div className="bg-slate-50 p-4 rounded-lg border border-slate-100">
            <p className="text-xs text-slate-500 font-medium uppercase">Total Budget</p>
            <p className="font-bold text-emerald-700 mt-1 text-lg">
              {trip_summary?.currency} {trip_summary?.budget?.toLocaleString() || "Flexible"}
            </p>
            {budget && (
              <p className="text-xs text-slate-500 mt-0.5">
                Est: {budget.currency} {budget.total?.toLocaleString()}
              </p>
            )}
          </div>
          <div className="bg-slate-50 p-4 rounded-lg border border-slate-100">
            <p className="text-xs text-slate-500 font-medium uppercase">Interests</p>
            <div className="flex flex-wrap gap-1 mt-1">
              {trip_summary?.interests && trip_summary.interests.length > 0 ? (
                trip_summary.interests.slice(0, 3).map((int, i) => (
                  <span
                    key={i}
                    className="text-xs bg-white border border-slate-200 text-slate-700 px-2 py-0.5 rounded-full"
                  >
                    {int}
                  </span>
                ))
              ) : (
                <span className="text-xs text-slate-400">General Sightseeing</span>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Interactive Replanning Action Bar */}
      <div className="bg-gradient-to-r from-blue-900 to-indigo-900 rounded-xl p-6 text-white shadow-md">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h2 className="text-lg font-bold flex items-center gap-2">
              <span>⚡</span> Want to adjust this itinerary?
            </h2>
            <p className="text-blue-200 text-sm mt-0.5">
              Ask our multi-agent system to adapt transport, hotels, activities, or budget.
            </p>
          </div>
          <div className="flex flex-wrap gap-2">
            {[
              "Switch to flight",
              "Find cheaper accommodation",
              "Add more cultural sights",
              "Reduce overall budget",
            ].map((chip) => (
              <button
                key={chip}
                disabled={isReplanning}
                onClick={() => handleReplanSubmit(chip)}
                className="text-xs bg-white/10 hover:bg-white/20 border border-white/20 px-3 py-1.5 rounded-full transition disabled:opacity-50"
              >
                + {chip}
              </button>
            ))}
          </div>
        </div>
        <div className="mt-4 flex gap-2">
          <input
            type="text"
            value={replanMessage}
            onChange={(e) => setReplanMessage(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleReplanSubmit()}
            placeholder="e.g. 'Prefer morning departure and 4-star boutique hotel'..."
            disabled={isReplanning}
            className="flex-1 px-4 py-2.5 rounded-lg bg-white/10 border border-white/20 text-white placeholder-blue-300 focus:outline-none focus:ring-2 focus:ring-blue-400 text-sm"
          />
          <button
            onClick={() => handleReplanSubmit()}
            disabled={isReplanning || !replanMessage.trim()}
            className="bg-blue-500 hover:bg-blue-600 text-white font-medium px-5 py-2.5 rounded-lg text-sm transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-1.5 flex-shrink-0"
          >
            {isReplanning ? (
              <>
                <div className="h-4 w-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                <span>Replanning...</span>
              </>
            ) : (
              <span>Replan Trip</span>
            )}
          </button>
        </div>
      </div>

      {/* Validation Warnings */}
      {validation && (!validation.is_valid || validation.warnings?.length > 0) && (
        <div className="bg-amber-50 border-l-4 border-amber-500 p-4 rounded-lg shadow-sm">
          <h3 className="text-amber-800 font-bold mb-1">Plan Notice</h3>
          {validation.errors?.length > 0 && (
            <ul className="list-disc pl-5 text-red-700 text-sm mb-2">
              {validation.errors.map((err, i) => (
                <li key={i}>{err}</li>
              ))}
            </ul>
          )}
          {validation.warnings?.length > 0 && (
            <ul className="list-disc pl-5 text-amber-700 text-sm">
              {validation.warnings.map((warn, i) => (
                <li key={i}>{warn}</li>
              ))}
            </ul>
          )}
        </div>
      )}

      {/* Transportation Section — Comparison Matrix & Selected Option */}
      {transportation && (
        <div className="bg-white p-6 sm:p-8 rounded-xl shadow-sm border border-gray-100">
          <div className="flex items-center justify-between mb-4 pb-3 border-b">
            <div>
              <h2 className="text-2xl font-bold text-gray-900">Transportation Comparison</h2>
              <p className="text-sm text-gray-500">
                Multi-agent evaluation across Bus, Train, and Flight options
              </p>
            </div>
            {transportation.recommendation_reason && (
              <span className="hidden md:inline-block text-xs bg-blue-50 text-blue-700 border border-blue-200 px-3 py-1 rounded-md max-w-sm text-right">
                💡 {transportation.recommendation_reason}
              </span>
            )}
          </div>

          {/* Selected Option Spotlight */}
          <div className="bg-emerald-50/60 border-2 border-emerald-500/40 rounded-xl p-5 mb-6 relative">
            <div className="flex flex-wrap items-center justify-between gap-2 mb-3">
              <div className="flex items-center gap-2">
                <span className="bg-emerald-600 text-white text-xs font-bold px-2.5 py-1 rounded-md uppercase tracking-wider">
                  ★ Agent Selected Choice
                </span>
                <span className="text-xs font-semibold text-emerald-800 uppercase">
                  {transportation.selected.mode}
                </span>
                {renderSourceBadge(transportation.selected.source_type)}
              </div>
              <div className="text-right">
                <span className="text-xl font-extrabold text-emerald-700">
                  {trip_summary?.currency || "INR"} {transportation.selected.total_price?.toLocaleString()}
                </span>
                <span className="text-xs text-gray-500 block">
                  ({trip_summary?.currency || "INR"} {transportation.selected.price_per_person?.toLocaleString()} / person)
                </span>
              </div>
            </div>

            <div className="grid sm:grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <p className="text-xs text-gray-500 uppercase font-medium">Provider & Vehicle</p>
                <p className="font-bold text-gray-900">{transportation.selected.provider}</p>
                <p className="text-xs text-gray-600">{transportation.selected.vehicle_info || "Standard Coach"}</p>
              </div>
              <div>
                <p className="text-xs text-gray-500 uppercase font-medium">Schedule</p>
                <p className="font-semibold text-gray-900">
                  {transportation.selected.departure_time || "Morning"} → {transportation.selected.arrival_time || "Evening"}
                </p>
                {transportation.selected.duration_minutes && (
                  <p className="text-xs text-gray-600">
                    {Math.floor(transportation.selected.duration_minutes / 60)}h {transportation.selected.duration_minutes % 60}m duration
                  </p>
                )}
              </div>
              <div>
                <p className="text-xs text-gray-500 uppercase font-medium">Comfort & Stops</p>
                <p className="font-semibold text-gray-900 capitalize">
                  {transportation.selected.comfort_level} Class
                </p>
                <p className="text-xs text-gray-600">
                  {transportation.selected.stops === 0 ? "Non-stop direct" : `${transportation.selected.stops} stop(s)`}
                </p>
              </div>
              <div>
                <p className="text-xs text-gray-500 uppercase font-medium">Availability</p>
                <p className="font-semibold text-emerald-700">
                  {transportation.selected.availability || "Confirmed"}
                </p>
                <p className="text-xs text-gray-500">Source: {transportation.selected.source}</p>
              </div>
            </div>

            {/* Decision Factors */}
            {transportation.selected.decision_factors && (
              <div className="mt-4 pt-3 border-t border-emerald-200/60">
                <span className="text-xs font-semibold text-emerald-900 mr-2">Evaluation Metrics:</span>
                {formatDecisionFactors(transportation.selected.decision_factors)}
              </div>
            )}
          </div>

          {/* Alternatives Table */}
          {transportation.alternatives && transportation.alternatives.length > 0 && (
            <div>
              <h3 className="text-sm font-bold text-gray-700 uppercase tracking-wider mb-3">
                Evaluated Alternatives ({transportation.alternatives.length})
              </h3>
              <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
                {transportation.alternatives.map((alt: TransportOption, idx: number) => (
                  <div
                    key={alt.id || idx}
                    className="border border-gray-200 rounded-lg p-4 bg-gray-50/50 hover:bg-white hover:border-gray-300 transition"
                  >
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-bold text-sm text-gray-800 uppercase flex items-center gap-1.5">
                        <span>{alt.mode === "flight" ? "✈" : alt.mode === "train" ? "🚆" : "🚌"}</span>
                        {alt.mode}
                      </span>
                      {renderSourceBadge(alt.source_type)}
                    </div>
                    <p className="text-xs font-semibold text-gray-700">{alt.provider}</p>
                    <p className="text-xs text-gray-500 mb-2">{alt.vehicle_info}</p>
                    <div className="flex justify-between items-baseline mb-2">
                      <span className="text-xs text-gray-500">
                        {alt.duration_minutes
                          ? `${Math.floor(alt.duration_minutes / 60)}h ${alt.duration_minutes % 60}m`
                          : "Scheduled"}
                      </span>
                      <span className="font-bold text-sm text-gray-900">
                        {trip_summary?.currency || "INR"} {alt.total_price?.toLocaleString()}
                      </span>
                    </div>
                    <div className="pt-2 border-t border-gray-200">
                      {formatDecisionFactors(alt.decision_factors)}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Accommodation Section */}
      {accommodation && (
        <div className="bg-white p-6 sm:p-8 rounded-xl shadow-sm border border-gray-100">
          <div className="flex items-center justify-between mb-4 pb-3 border-b">
            <div>
              <h2 className="text-2xl font-bold text-gray-900">Accommodation</h2>
              <p className="text-sm text-gray-500">Selected stay and evaluated alternatives</p>
            </div>
            {renderSourceBadge(accommodation.source_type)}
          </div>

          <div className="bg-blue-50/50 border border-blue-200 rounded-xl p-5 mb-6">
            <div className="flex flex-wrap items-start justify-between gap-3 mb-3">
              <div>
                <span className="bg-blue-600 text-white text-xs font-bold px-2.5 py-1 rounded uppercase tracking-wider mr-2">
                  Selected Stay
                </span>
                <h3 className="text-xl font-bold inline-block text-gray-900 mt-1">
                  {accommodation.name}
                </h3>
                <p className="text-sm text-gray-600 mt-1">
                  📍 {accommodation.location}
                  {accommodation.rating && (
                    <span className="ml-3 text-amber-600 font-semibold">
                      ★ {accommodation.rating} / 5.0
                    </span>
                  )}
                </p>
              </div>
              <div className="text-right">
                <span className="text-2xl font-extrabold text-blue-900">
                  {trip_summary?.currency || "INR"} {accommodation.total_price?.toLocaleString()}
                </span>
                <span className="text-xs text-gray-500 block">
                  ({trip_summary?.currency || "INR"} {accommodation.nightly_price?.toLocaleString()} / night)
                </span>
              </div>
            </div>

            {accommodation.room_type && (
              <p className="text-sm text-gray-700 mb-2">
                <span className="font-semibold">Room:</span> {accommodation.room_type}
              </p>
            )}

            {accommodation.amenities && accommodation.amenities.length > 0 && (
              <div className="flex flex-wrap gap-1.5 mt-3">
                {accommodation.amenities.map((amenity, i) => (
                  <span
                    key={i}
                    className="text-xs bg-white border border-blue-200 text-blue-900 px-2.5 py-0.5 rounded-full"
                  >
                    ✓ {amenity}
                  </span>
                ))}
              </div>
            )}
          </div>

          {/* Accommodation Alternatives */}
          {accommodation_alternatives && accommodation_alternatives.length > 0 && (
            <div>
              <h3 className="text-sm font-bold text-gray-700 uppercase tracking-wider mb-3">
                Alternative Accommodations ({accommodation_alternatives.length})
              </h3>
              <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
                {accommodation_alternatives.map((alt: AccommodationOption, idx: number) => (
                  <div
                    key={alt.id || idx}
                    className="border border-gray-200 rounded-lg p-4 bg-gray-50/50 hover:bg-white transition"
                  >
                    <div className="flex justify-between items-start mb-1">
                      <h4 className="font-bold text-sm text-gray-900">{alt.name}</h4>
                      {renderSourceBadge(alt.source_type)}
                    </div>
                    <p className="text-xs text-gray-500 mb-2">📍 {alt.location}</p>
                    <div className="flex justify-between items-center text-xs">
                      <span className="text-amber-600 font-medium">
                        {alt.rating ? `★ ${alt.rating}` : "Unrated"}
                      </span>
                      <span className="font-bold text-gray-900">
                        {trip_summary?.currency || "INR"} {alt.total_price?.toLocaleString()}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Activities & Attractions */}
      {activities && activities.length > 0 && (
        <div className="bg-white p-6 sm:p-8 rounded-xl shadow-sm border border-gray-100">
          <div className="flex items-center justify-between mb-4 pb-3 border-b">
            <div>
              <h2 className="text-2xl font-bold text-gray-900">Attractions & Experiences</h2>
              <p className="text-sm text-gray-500">
                Recommended activities tailored to {trip_summary?.interests?.join(", ") || "your interests"}
              </p>
            </div>
            <span className="text-xs bg-purple-100 text-purple-800 font-semibold px-2.5 py-1 rounded-full">
              {activities.length} Curated Options
            </span>
          </div>

          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {activities.map((act, idx) => (
              <div
                key={act.id || idx}
                className="border border-gray-200 rounded-xl p-4 bg-white hover:shadow-sm transition"
              >
                <div className="flex justify-between items-start gap-2 mb-2">
                  <span className="text-xs font-semibold uppercase tracking-wider text-purple-700 bg-purple-50 px-2 py-0.5 rounded">
                    {act.category}
                  </span>
                  {renderSourceBadge(act.source_type)}
                </div>
                <h3 className="font-bold text-gray-900 text-base mb-1">{act.name}</h3>
                {act.description && (
                  <p className="text-xs text-gray-600 mb-3 line-clamp-2">{act.description}</p>
                )}
                <div className="flex justify-between items-center pt-2 border-t border-gray-100 text-xs text-gray-500">
                  <span>
                    {act.estimated_duration_minutes
                      ? `⏱ ${act.estimated_duration_minutes} min`
                      : "Flexible time"}
                  </span>
                  <span className="font-bold text-gray-900">
                    {act.estimated_cost && act.estimated_cost > 0
                      ? `${trip_summary?.currency || "INR"} ${act.estimated_cost}`
                      : "Free Admission"}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Two Column: Budget Breakdown & Weather Forecast */}
      <div className="grid md:grid-cols-2 gap-8">
        {/* Budget */}
        {budget && (
          <div className="bg-white p-6 sm:p-8 rounded-xl shadow-sm border border-gray-100 flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-4 pb-3 border-b">
                <h2 className="text-xl font-bold text-gray-900">Budget Breakdown</h2>
                <span
                  className={`text-xs font-bold px-2.5 py-1 rounded uppercase ${
                    budget.status === "within_budget"
                      ? "bg-emerald-100 text-emerald-800"
                      : budget.status === "near_budget"
                      ? "bg-amber-100 text-amber-800"
                      : "bg-red-100 text-red-800"
                  }`}
                >
                  {budget.status?.replace(/_/g, " ")}
                </span>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full text-left text-sm">
                  <thead>
                    <tr className="border-b text-gray-500 text-xs uppercase">
                      <th className="py-2">Category</th>
                      <th className="py-2 text-right">Amount ({budget.currency})</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                    <tr>
                      <td className="py-2 text-gray-700">Transportation</td>
                      <td className="py-2 text-right font-medium">{budget.transportation?.toLocaleString()}</td>
                    </tr>
                    <tr>
                      <td className="py-2 text-gray-700">Accommodation</td>
                      <td className="py-2 text-right font-medium">{budget.accommodation?.toLocaleString()}</td>
                    </tr>
                    <tr>
                      <td className="py-2 text-gray-700">Food & Dining</td>
                      <td className="py-2 text-right font-medium">{budget.food?.toLocaleString()}</td>
                    </tr>
                    <tr>
                      <td className="py-2 text-gray-700">Activities & Sightseeing</td>
                      <td className="py-2 text-right font-medium">{budget.activities?.toLocaleString()}</td>
                    </tr>
                    <tr>
                      <td className="py-2 text-gray-700">Local Transport</td>
                      <td className="py-2 text-right font-medium">{budget.local_transport?.toLocaleString()}</td>
                    </tr>
                    <tr>
                      <td className="py-2 text-gray-700">Miscellaneous & Contingency</td>
                      <td className="py-2 text-right font-medium">{budget.miscellaneous?.toLocaleString()}</td>
                    </tr>
                    <tr className="font-extrabold text-base bg-slate-50">
                      <td className="py-3 px-2 text-gray-900">Total Estimated Cost</td>
                      <td className="py-3 px-2 text-right text-emerald-700">
                        {budget.currency} {budget.total?.toLocaleString()}
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>

              {budget.per_person_total && (
                <p className="text-xs text-gray-500 text-right mt-2">
                  Per person: {budget.currency} {budget.per_person_total.toLocaleString()}
                </p>
              )}
            </div>

            {budget.optimization_suggestions && budget.optimization_suggestions.length > 0 && (
              <div className="mt-4 pt-3 border-t border-gray-100 bg-blue-50/50 p-3 rounded-lg">
                <p className="text-xs font-bold text-blue-900 mb-1">💡 Budget Insights:</p>
                <ul className="list-disc pl-4 text-xs text-blue-800 space-y-0.5">
                  {budget.optimization_suggestions.map((sug, i) => (
                    <li key={i}>{sug}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}

        {/* Weather */}
        {weather && (
          <div className="bg-white p-6 sm:p-8 rounded-xl shadow-sm border border-gray-100 flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-4 pb-3 border-b">
                <div>
                  <h2 className="text-xl font-bold text-gray-900">Weather Outlook</h2>
                  <p className="text-xs text-gray-500">Destination Forecast</p>
                </div>
                {renderSourceBadge(weather.source_type)}
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                {weather.days?.map((day, idx) => (
                  <div
                    key={idx}
                    className="border border-slate-100 rounded-xl p-3 text-center bg-slate-50/70"
                  >
                    <p className="font-bold text-xs text-gray-700">{day.date}</p>
                    <div className="my-1 text-2xl">
                      {day.condition?.toLowerCase().includes("sun")
                        ? "☀️"
                        : day.condition?.toLowerCase().includes("rain")
                        ? "🌧️"
                        : "⛅"}
                    </div>
                    <p className="text-xs font-bold text-gray-900">
                      {day.temperature_high}° / {day.temperature_low}°C
                    </p>
                    <p className="text-[11px] text-gray-500 capitalize mt-0.5">{day.condition}</p>
                  </div>
                ))}
              </div>
            </div>

            {weather.overall_recommendation && (
              <div className="mt-4 pt-3 border-t border-gray-100 bg-amber-50/60 p-3 rounded-lg">
                <p className="text-xs font-bold text-amber-900 mb-0.5">🌦 Advisory:</p>
                <p className="text-xs text-amber-800">{weather.overall_recommendation}</p>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Day-by-Day Itinerary */}
      {itinerary && (
        <div className="bg-white p-6 sm:p-8 rounded-xl shadow-sm border border-gray-100">
          <div className="flex items-center justify-between mb-6 pb-3 border-b">
            <div>
              <h2 className="text-2xl font-bold text-gray-900">Day-by-Day Schedule</h2>
              <p className="text-sm text-gray-500">
                Coordinated timeline with transit, stays, and attractions
              </p>
            </div>
            <span className="text-xs bg-blue-100 text-blue-800 font-semibold px-3 py-1 rounded-full">
              {itinerary.total_days} Days Planned
            </span>
          </div>

          <div className="space-y-6">
            {itinerary.days?.map((day, idx) => (
              <div
                key={idx}
                className="border border-gray-200 rounded-xl p-5 bg-white relative overflow-hidden"
              >
                <div className="flex flex-wrap items-center justify-between gap-2 pb-3 mb-4 border-b border-gray-100">
                  <div className="flex items-center gap-3">
                    <span className="bg-blue-600 text-white font-bold text-xs px-2.5 py-1 rounded-md">
                      Day {day.day_number}
                    </span>
                    {day.date && <span className="text-sm text-gray-500 font-medium">{day.date}</span>}
                  </div>
                  {day.theme && (
                    <span className="text-xs font-semibold text-blue-700 bg-blue-50 px-3 py-0.5 rounded-full">
                      {day.theme}
                    </span>
                  )}
                </div>

                <div className="space-y-4">
                  {day.items?.map((item, i) => (
                    <div key={i} className="flex items-start gap-4">
                      <div className="text-xs font-bold text-gray-500 w-24 flex-shrink-0 pt-0.5">
                        {item.time_start || "Flexible"}
                        {item.time_end ? ` - ${item.time_end}` : ""}
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          <h4 className="font-bold text-sm text-gray-900">{item.title}</h4>
                          <span className="text-[10px] uppercase font-bold text-slate-500 bg-slate-100 px-1.5 py-0.2 rounded">
                            {item.item_type}
                          </span>
                        </div>
                        {item.description && (
                          <p className="text-xs text-gray-600 mt-1">{item.description}</p>
                        )}
                        <div className="flex items-center gap-4 text-xs text-gray-400 mt-1">
                          {item.location && <span>📍 {item.location}</span>}
                          {item.estimated_cost && item.estimated_cost > 0 ? (
                            <span className="text-gray-600 font-medium">
                              Est: {trip_summary?.currency || "INR"} {item.estimated_cost}
                            </span>
                          ) : null}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>

                {day.notes && (
                  <p className="text-xs text-slate-500 mt-4 pt-3 border-t border-dashed border-gray-200">
                    ℹ {day.notes}
                  </p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Data Source & Provenance Transparency Footer */}
      <div className="bg-slate-50 rounded-xl p-5 border border-slate-200 text-xs text-slate-600">
        <h4 className="font-bold text-slate-800 uppercase tracking-wider mb-2">
          System Transparency & Data Provenance
        </h4>
        <p className="mb-2">
          This plan was generated via multi-agent collaborative synthesis (LangGraph orchestration).
        </p>
        <div className="flex flex-wrap gap-2">
          {data_sources && data_sources.length > 0 ? (
            data_sources.map((src, i) => (
              <span
                key={i}
                className="bg-white border border-slate-200 text-slate-700 px-2 py-1 rounded"
              >
                {src.provider}: <strong>{src.source_type}</strong>
              </span>
            ))
          ) : (
            <span className="bg-white border border-slate-200 text-slate-700 px-2 py-1 rounded">
              Mock Providers Active for Academic Demonstration
            </span>
          )}
        </div>
      </div>
    </div>
  );
}
