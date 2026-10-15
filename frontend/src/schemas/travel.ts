/**
 * Zod schemas for frontend form validation.
 */
import { z } from "zod";

export const travelPlanSchema = z.object({
  raw_request: z.string().optional(),
  origin: z.string().min(1, "Origin is required").optional(),
  destination: z.string().min(1, "Destination is required").optional(),
  departure_date: z.string().optional(),
  return_date: z.string().optional(),
  travelers: z.number().int().min(1).max(20).optional(),
  budget: z.number().positive().optional(),
  currency: z.string().default("INR"),
  travel_style: z
    .enum(["budget", "standard", "premium", "luxury", "custom"])
    .default("standard"),
  preferred_transport: z.array(z.string()).default([]),
  interests: z.array(z.string()).default([]),
  accommodation_preference: z.string().optional(),
  output_detail: z.enum(["brief", "standard", "detailed"]).default("standard"),
  additional_requirements: z.string().optional(),
});

export type TravelPlanFormData = z.infer<typeof travelPlanSchema>;
