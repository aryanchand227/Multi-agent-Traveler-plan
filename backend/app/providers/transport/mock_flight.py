"""Mock flight transport provider."""
import datetime
import hashlib
from typing import List

from app.schemas.transport import (
    FlightOption,
    ComfortLevel,
    ProviderType,
    SourceType,
    TransportMode,
    TransportOption
)
from app.providers.transport.base import FlightProvider


class MockFlightProvider(FlightProvider):
    def get_provider_name(self) -> str:
        return "MockFlight"

    async def search(
        self,
        origin: str,
        destination: str,
        date: str,
        travelers: int = 1,
    ) -> List[TransportOption]:
        # Deterministic generation
        seed_str = f"flight-{origin}-{destination}-{date}"
        seed = int(hashlib.md5(seed_str.encode()).hexdigest(), 16)
        
        flight_configs = [
            {"airline": "IndiGo", "code": "6E", "comfort": ComfortLevel.STANDARD, "price": 3500, "duration": 120},
            {"airline": "Air India", "code": "AI", "comfort": ComfortLevel.PREMIUM, "price": 5000, "duration": 130},
            {"airline": "Vistara", "code": "UK", "comfort": ComfortLevel.LUXURY, "price": 6500, "duration": 125},
            {"airline": "SpiceJet", "code": "SG", "comfort": ComfortLevel.ECONOMY, "price": 3000, "duration": 135},
            {"airline": "AirAsia India", "code": "I5", "comfort": ComfortLevel.ECONOMY, "price": 3200, "duration": 130},
        ]
        
        num_options = 3 + (seed % 3) # 3 to 5 options
        
        options = []
        for i in range(num_options):
            config_idx = (seed + i) % len(flight_configs)
            config = flight_configs[config_idx]
            
            # vary price a bit
            price_variation = (seed + i) % 500
            price_per_person = float(config["price"] + price_variation)
            
            flight_number = f"{config['code']}-{(seed + i) % 1000:03d}"
            
            options.append(FlightOption(
                id=f"flight-{flight_number}-{date}",
                mode=TransportMode.FLIGHT,
                provider=config["airline"],
                provider_type=ProviderType.AIRLINE,
                origin=origin,
                destination=destination,
                departure_time=f"{date}T{(6 + i * 4) % 24:02d}:00:00",
                arrival_time=f"{date}T{(6 + i * 4 + (config['duration'] // 60)) % 24:02d}:{config['duration'] % 60:02d}:00",
                duration_minutes=config["duration"],
                price_per_person=price_per_person,
                total_price=price_per_person * travelers,
                stops=0 if (seed + i) % 3 != 0 else 1,
                comfort_level=config["comfort"],
                vehicle_info=flight_number,
                availability="high",
                source=self.get_provider_name(),
                source_type=SourceType.MOCK,
                retrieved_at=datetime.datetime.now(datetime.timezone.utc),
                airline=config["airline"],
                flight_number=flight_number,
                departure_airport=f"{origin.upper()[:3]}",
                arrival_airport=f"{destination.upper()[:3]}",
                baggage_info="15kg Check-in, 7kg Cabin"
            ))
            
        return options
