export type AccommodationType =
  | "hostel"
  | "budget_hotel"
  | "guesthouse"
  | "hotel_3star"
  | "hotel_4star"
  | "hotel_5star"
  | "resort";

export interface AccommodationOption {
  id: string;
  name: string;
  location: string;
  accommodation_type: AccommodationType;
  rating?: number;
  nightly_price: number;
  total_price: number;
  amenities: string[];
  room_type?: string;
  source: string;
  source_type: "mock" | "live" | "cached";
  availability: string;
  retrieved_at: string;
  is_selected: boolean;
}
