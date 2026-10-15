"use client";

import React, { useState } from "react";
import type { ClarificationQuestion } from "@/types/travel";

interface ClarificationDialogProps {
  questions: ClarificationQuestion[];
  onSubmit: (responses: Record<string, string>) => void;
  isLoading: boolean;
}

export default function ClarificationDialog({ questions, onSubmit, isLoading }: ClarificationDialogProps) {
  const [responses, setResponses] = useState<Record<string, string>>({});

  const handleChange = (field: string, value: string) => {
    setResponses((prev) => ({ ...prev, [field]: value }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(responses);
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg p-6 max-w-lg w-full text-gray-900 shadow-xl max-h-[90vh] overflow-y-auto">
        <h2 className="text-xl font-bold mb-4">We need a few more details</h2>
        <form onSubmit={handleSubmit} className="space-y-6">
          {questions.map((q) => (
            <div key={q.field}>
              <label className="block text-sm font-medium mb-1">
                {q.question} {q.required && <span className="text-red-500">*</span>}
              </label>
              {q.options && q.options.length > 0 ? (
                <select
                  required={q.required}
                  value={responses[q.field] || ""}
                  onChange={(e) => handleChange(q.field, e.target.value)}
                  className="w-full p-2 border rounded focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Select an option...</option>
                  {q.options.map((opt) => (
                    <option key={opt} value={opt}>
                      {opt}
                    </option>
                  ))}
                </select>
              ) : (
                <input
                  type="text"
                  required={q.required}
                  value={responses[q.field] || ""}
                  onChange={(e) => handleChange(q.field, e.target.value)}
                  className="w-full p-2 border rounded focus:ring-2 focus:ring-blue-500"
                  placeholder="Your answer..."
                />
              )}
            </div>
          ))}

          <div className="pt-4 flex justify-end gap-3">
            <button
              type="submit"
              disabled={isLoading}
              className="bg-blue-600 text-white font-bold py-2 px-6 rounded hover:bg-blue-700 disabled:opacity-50"
            >
              {isLoading ? "Submitting..." : "Submit Answers"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
