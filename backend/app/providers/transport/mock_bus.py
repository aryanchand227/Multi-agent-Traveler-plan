"""Mock bus transport provider."""
import datetime
import hashlib
from typing import List

from app.schemas.transport import (
    BusOption,
    ComfortLevel,
    ProviderType,
    SourceType,
    TransportMode,
    TransportOption
)
from app.providers.transport.base import BusProvider


class MockBusProvider(BusProvider):
    def get_provider_name(self) -> str:
        return "MockBus"

    async def search(
        self,
        origin: str,
        destination: str,
        date: str,
        travelers: int = 1,
    ) -> List[TransportOption]:
        # Deterministic generation
        seed_str = f"bus-{origin}-{destination}-{date}"
        seed = int(hashlib.md5(seed_str.encode()).hexdigest(), 16)
        
        bus_configs = [
            {"provider": "APSRTC", "provider_type": ProviderType.GOVERNMENT, "bus_type": "Ordinary", "comfort": ComfortLevel.ECONOMY, "price": 450, "duration": 14 * 60},
            {"provider": "KSRTC", "provider_type": ProviderType.GOVERNMENT, "bus_type": "Semi-Sleeper", "comfort": ComfortLevel.STANDARD, "price": 600, "duration": 12 * 60},
            {"provider": "GSRTC", "provider_type": ProviderType.GOVERNMENT, "bus_type": "AC Sleeper", "comfort": ComfortLevel.PREMIUM, "price": 1200, "duration": 11 * 60},
            {"provider": "VRL", "provider_type": ProviderType.PRIVATE, "bus_type": "Sleeper", "comfort": ComfortLevel.STANDARD, "price": 900, "duration": 12 * 60},
            {"provider": "SRS", "provider_type": ProviderType.PRIVATE, "bus_type": "AC Sleeper", "comfort": ComfortLevel.PREMIUM, "price": 1400, "duration": 10 * 60},
            {"provider": "Orange", "provider_type": ProviderType.PRIVATE, "bus_type": "Volvo AC", "comfort": ComfortLevel.LUXURY, "price": 2000, "duration": 9 * 60},
        ]
        
        num_options = 3 + (seed % 3) # 3 to 5 options
        
        options = []
        for i in range(num_options):
            config_idx = (seed + i) % len(bus_configs)
            config = bus_configs[config_idx]
            
            # vary price a bit
            price_variation = (seed + i) % 100
            price_per_person = float(config["price"] + price_variation)
            
            options.append(BusOption(
                id=f"bus-{seed % 10000}-{i}",
                mode=TransportMode.BUS,
                provider=config["provider"],
                provider_type=config["provider_type"],
                origin=origin,
                destination=destination,
                departure_time=f"{date}T{(8 + i) % 24:02d}:00:00",
                arrival_time=f"{date}T{(8 + i + (config['duration'] // 60)) % 24:02d}:00:00",
                duration_minutes=config["duration"],
                price_per_person=price_per_person,
                total_price=price_per_person * travelers,
                stops=0,
                comfort_level=config["comfort"],
                vehicle_info=f"{config['provider']} {config['bus_type']}",
                availability="high",
                source=self.get_provider_name(),
                source_type=SourceType.MOCK,
                retrieved_at=datetime.datetime.now(datetime.timezone.utc),
                bus_type=config["bus_type"],
                operator_type=config["provider_type"].value
            ))
            
        return options
