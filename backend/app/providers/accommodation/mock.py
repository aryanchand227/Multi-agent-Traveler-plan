"""Mock accommodation provider."""
from __future__ import annotations

import datetime
import uuid

from app.providers.accommodation.base import AccommodationProvider
from app.schemas.accommodation import AccommodationOption, AccommodationType
from app.schemas.transport import SourceType


class MockAccommodationProvider(AccommodationProvider):
    """Mock implementation of AccommodationProvider."""

    async def search(
        self,
        destination: str,
        check_in: str,
        check_out: str,
        travelers: int = 1,
        budget_per_night: float | None = None,
        travel_style: str = "standard",
    ) -> list[AccommodationOption]:
        """Search for accommodation options."""
        dest_lower = destination.lower()
        options = []
        
        # Define mock inventory
        inventory = {
            "budget": [
                {
                    "name": f"Backpackers Hostel {destination}",
                    "type": AccommodationType.HOSTEL,
                    "price": 800,
                    "rating": 4.1,
                    "amenities": ["Free Wi-Fi", "Bunk Beds", "Shared Kitchen"]
                },
                {
                    "name": f"Budget Inn {destination}",
                    "type": AccommodationType.BUDGET_HOTEL,
                    "price": 1200,
                    "rating": 3.8,
                    "amenities": ["Free Wi-Fi", "AC", "Private Bathroom"]
                }
            ],
            "standard": [
                {
                    "name": f"City Center Hotel {destination}",
                    "type": AccommodationType.HOTEL_3STAR,
                    "price": 2500,
                    "rating": 4.3,
                    "amenities": ["Free Wi-Fi", "AC", "Breakfast Included", "TV"]
                },
                {
                    "name": f"{destination} Comfort Stay",
                    "type": AccommodationType.HOTEL_3STAR,
                    "price": 3200,
                    "rating": 4.5,
                    "amenities": ["Free Wi-Fi", "AC", "Restaurant", "Room Service"]
                }
            ],
            "premium": [
                {
                    "name": f"Grand {destination} Hotel",
                    "type": AccommodationType.HOTEL_4STAR,
                    "price": 6000,
                    "rating": 4.7,
                    "amenities": ["Pool", "Spa", "Gym", "Breakfast Included", "Bar"]
                },
                {
                    "name": f"Boutique {destination} Suites",
                    "type": AccommodationType.HOTEL_4STAR,
                    "price": 7500,
                    "rating": 4.8,
                    "amenities": ["Premium Wi-Fi", "Concierge", "Lounge", "Valet"]
                }
            ],
            "luxury": [
                {
                    "name": f"The Taj {destination}",
                    "type": AccommodationType.HOTEL_5STAR,
                    "price": 15000,
                    "rating": 4.9,
                    "amenities": ["Luxury Spa", "Multiple Restaurants", "Infinity Pool", "Butler Service"]
                },
                {
                    "name": f"{destination} Palace Resort",
                    "type": AccommodationType.RESORT,
                    "price": 22000,
                    "rating": 4.9,
                    "amenities": ["Private Beach/Garden", "All-Inclusive", "Golf Course", "Helipad"]
                }
            ]
        }
        
        # Calculate nights
        try:
            ci_date = datetime.datetime.strptime(check_in, "%Y-%m-%d").date()
            co_date = datetime.datetime.strptime(check_out, "%Y-%m-%d").date()
            nights = max(1, (co_date - ci_date).days)
        except ValueError:
            nights = 1

        selected_category = travel_style.lower()
        if selected_category not in inventory:
            selected_category = "standard"
            
        # If a budget is provided, filter or adjust
        items = inventory.get(selected_category, [])
        
        for item in items:
            nightly_price = item["price"]
            
            # If the user specified a strict budget that is lower, skip or we just include it as options anyway
            # but since it's mock, we'll return the ones matching the travel_style primarily
            
            total_price = nightly_price * nights * ((travelers + 1) // 2)  # Assuming 2 people per room
            
            options.append(
                AccommodationOption(
                    id=str(uuid.uuid4()),
                    name=item["name"],
                    location=f"Central {destination}",
                    accommodation_type=item["type"],
                    rating=item["rating"],
                    nightly_price=nightly_price,
                    total_price=total_price,
                    amenities=item["amenities"],
                    room_type="Standard Room",
                    source="MockAccommodationAPI",
                    source_type=SourceType.MOCK,
                    availability="available",
                    retrieved_at=datetime.datetime.now(datetime.timezone.utc)
                )
            )
            
        # Ensure we return 4-6 options by adding standard if luxury/premium
        if len(options) < 4:
            alt_category = "standard" if selected_category != "standard" else "budget"
            for item in inventory.get(alt_category, []):
                nightly_price = item["price"]
                total_price = nightly_price * nights * ((travelers + 1) // 2)
                options.append(
                    AccommodationOption(
                        id=str(uuid.uuid4()),
                        name=item["name"],
                        location=f"Near City Center, {destination}",
                        accommodation_type=item["type"],
                        rating=item["rating"],
                        nightly_price=nightly_price,
                        total_price=total_price,
                        amenities=item["amenities"],
                        room_type="Standard Room",
                        source="MockAccommodationAPI",
                        source_type=SourceType.MOCK,
                        availability="available",
                        retrieved_at=datetime.datetime.now(datetime.timezone.utc)
                    )
                )

        return options

    def get_provider_name(self) -> str:
        return "Mock Accommodation Provider"
