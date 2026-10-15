"use client";

import React, { useState } from "react";
import type { TravelPlanRequest, TravelStyle } from "@/types/travel";

interface PlanFormProps {
  onSubmit: (data: TravelPlanRequest) => void;
  isLoading: boolean;
}

export default function PlanForm({ onSubmit, isLoading }: PlanFormProps) {
  const [formData, setFormData] = useState<TravelPlanRequest>({
    raw_request: "",
    origin: "",
    destination: "",
    departure_date: "",
    return_date: "",
    travelers: 1,
    budget: undefined,
    travel_style: "standard",
    preferred_transport: [],
    interests: [],
  });

  const [interestsText, setInterestsText] = useState("");

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>
  ) => {
    const { name, value, type } = e.target;

    if (type === "number") {
      setFormData((prev) => ({ ...prev, [name]: value ? Number(value) : undefined }));
    } else {
      setFormData((prev) => ({ ...prev, [name]: value }));
    }
  };

  const handleTransportChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const options = Array.from(e.target.selectedOptions, (option) => option.value);
    setFormData((prev) => ({ ...prev, preferred_transport: options }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const interests = interestsText
      .split(",")
      .map((s) => s.trim())
      .filter((s) => s.length > 0);
    onSubmit({
      ...formData,
      interests,
    });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6 max-w-2xl mx-auto p-6 bg-white shadow rounded-lg text-gray-900">
      <h2 className="text-2xl font-bold mb-4">Plan Your Trip</h2>

      <div>
        <label className="block text-sm font-medium mb-1">Natural Language Request</label>
        <textarea
          name="raw_request"
          value={formData.raw_request}
          onChange={handleChange}
          className="w-full p-2 border rounded focus:ring-2 focus:ring-blue-500"
          placeholder="I want to go to Goa from Hyderabad for a 3 day weekend..."
          rows={3}
        />
        <p className="text-xs text-gray-500 mt-1">If you provide this, we'll try to extract the details below automatically.</p>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium mb-1">Origin</label>
          <input
            type="text"
            name="origin"
            value={formData.origin || ""}
            onChange={handleChange}
            className="w-full p-2 border rounded focus:ring-2 focus:ring-blue-500"
            placeholder="e.g. Hyderabad"
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Destination</label>
          <input
            type="text"
            name="destination"
            value={formData.destination || ""}
            onChange={handleChange}
            className="w-full p-2 border rounded focus:ring-2 focus:ring-blue-500"
            placeholder="e.g. Goa"
          />
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium mb-1">Departure Date</label>
          <input
            type="date"
            name="departure_date"
            value={formData.departure_date || ""}
            onChange={handleChange}
            className="w-full p-2 border rounded focus:ring-2 focus:ring-blue-500"
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Return Date</label>
          <input
            type="date"
            name="return_date"
            value={formData.return_date || ""}
            onChange={handleChange}
            className="w-full p-2 border rounded focus:ring-2 focus:ring-blue-500"
          />
        </div>
      </div>

      <div className="grid grid-cols-3 gap-4">
        <div>
          <label className="block text-sm font-medium mb-1">Travelers</label>
          <input
            type="number"
            name="travelers"
            min="1"
            value={formData.travelers || ""}
            onChange={handleChange}
            className="w-full p-2 border rounded focus:ring-2 focus:ring-blue-500"
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Budget (INR)</label>
          <input
            type="number"
            name="budget"
            min="0"
            value={formData.budget || ""}
            onChange={handleChange}
            className="w-full p-2 border rounded focus:ring-2 focus:ring-blue-500"
            placeholder="e.g. 50000"
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Travel Style</label>
          <select
            name="travel_style"
            value={formData.travel_style || "standard"}
            onChange={handleChange}
            className="w-full p-2 border rounded focus:ring-2 focus:ring-blue-500"
          >
            <option value="budget">Budget</option>
            <option value="standard">Standard</option>
            <option value="premium">Premium</option>
            <option value="luxury">Luxury</option>
            <option value="custom">Custom</option>
          </select>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium mb-1">Preferred Transport (Multi)</label>
          <select
            multiple
            name="preferred_transport"
            value={formData.preferred_transport || []}
            onChange={handleTransportChange}
            className="w-full p-2 border rounded focus:ring-2 focus:ring-blue-500 h-24"
          >
            <option value="flight">Flight</option>
            <option value="train">Train</option>
            <option value="bus">Bus</option>
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Interests (Comma separated)</label>
          <textarea
            value={interestsText}
            onChange={(e) => setInterestsText(e.target.value)}
            className="w-full p-2 border rounded focus:ring-2 focus:ring-blue-500 h-24"
            placeholder="beaches, history, food..."
          />
        </div>
      </div>

      <button
        type="submit"
        disabled={isLoading}
        className="w-full bg-blue-600 text-white font-bold py-3 px-4 rounded hover:bg-blue-700 disabled:opacity-50"
      >
        {isLoading ? "Planning..." : "Plan My Trip"}
      </button>
    </form>
  );
}
