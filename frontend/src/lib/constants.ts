export const TRAVEL_STYLES = [
  { value: "budget", label: "Budget-Friendly", description: "Maximize savings" },
  { value: "standard", label: "Standard", description: "Balance of cost & comfort" },
  { value: "premium", label: "Premium", description: "Enhanced comfort" },
  { value: "luxury", label: "Luxury", description: "Best of everything" },
  { value: "custom", label: "Custom Budget", description: "Set your own budget" },
] as const;

export const TRANSPORT_MODES = [
  { value: "bus", label: "Bus", icon: "🚌" },
  { value: "train", label: "Train", icon: "🚂" },
  { value: "flight", label: "Flight", icon: "✈️" },
] as const;

export const INTERESTS = [
  { value: "adventure", label: "Adventure", icon: "🏔️" },
  { value: "beaches", label: "Beaches", icon: "🏖️" },
  { value: "cultural", label: "Cultural", icon: "🏛️" },
  { value: "food", label: "Food", icon: "🍜" },
  { value: "historical", label: "Historical", icon: "🏰" },
  { value: "nature", label: "Nature", icon: "🌿" },
  { value: "nightlife", label: "Nightlife", icon: "🌃" },
  { value: "shopping", label: "Shopping", icon: "🛍️" },
  { value: "relaxation", label: "Relaxation", icon: "🧘" },
  { value: "family", label: "Family", icon: "👨👩👧👦" },
] as const;

export const OUTPUT_DETAILS = [
  { value: "brief", label: "Brief", description: "Quick summary" },
  { value: "standard", label: "Standard", description: "Balanced detail" },
  { value: "detailed", label: "Detailed", description: "Comprehensive plan" },
] as const;
