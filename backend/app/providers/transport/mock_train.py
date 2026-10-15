"""Mock train transport provider."""
import datetime
import hashlib
from typing import List

from app.schemas.transport import (
    TrainOption,
    ComfortLevel,
    ProviderType,
    SourceType,
    TransportMode,
    TransportOption
)
from app.providers.transport.base import TrainProvider


class MockTrainProvider(TrainProvider):
    def get_provider_name(self) -> str:
        return "MockTrain"

    async def search(
        self,
        origin: str,
        destination: str,
        date: str,
        travelers: int = 1,
    ) -> List[TransportOption]:
        # Deterministic generation
        seed_str = f"train-{origin}-{destination}-{date}"
        seed = int(hashlib.md5(seed_str.encode()).hexdigest(), 16)
        
        train_configs = [
            {"name": "Rajdhani Express", "class": "1AC", "comfort": ComfortLevel.LUXURY, "price": 3500, "duration": 15 * 60},
            {"name": "Shatabdi Express", "class": "CC", "comfort": ComfortLevel.PREMIUM, "price": 1200, "duration": 8 * 60},
            {"name": "Duronto Express", "class": "2AC", "comfort": ComfortLevel.PREMIUM, "price": 2800, "duration": 14 * 60},
            {"name": "Garib Rath", "class": "3AC", "comfort": ComfortLevel.STANDARD, "price": 900, "duration": 16 * 60},
            {"name": "Superfast Express", "class": "SL", "comfort": ComfortLevel.ECONOMY, "price": 450, "duration": 18 * 60},
        ]
        
        num_options = 3 + (seed % 3) # 3 to 5 options
        
        options = []
        for i in range(num_options):
            config_idx = (seed + i) % len(train_configs)
            config = train_configs[config_idx]
            
            # vary price a bit
            price_variation = (seed + i) % 50
            price_per_person = float(config["price"] + price_variation)
            
            train_number = f"1{(seed + i) % 10000:04d}"
            
            options.append(TrainOption(
                id=f"train-{train_number}-{date}",
                mode=TransportMode.TRAIN,
                provider="Indian Railways",
                provider_type=ProviderType.GOVERNMENT,
                origin=origin,
                destination=destination,
                departure_time=f"{date}T{(10 + i) % 24:02d}:30:00",
                arrival_time=f"{date}T{(10 + i + (config['duration'] // 60)) % 24:02d}:30:00",
                duration_minutes=config["duration"],
                price_per_person=price_per_person,
                total_price=price_per_person * travelers,
                stops= (seed + i) % 5,
                comfort_level=config["comfort"],
                vehicle_info=f"{train_number} {config['name']}",
                availability="medium",
                source=self.get_provider_name(),
                source_type=SourceType.MOCK,
                retrieved_at=datetime.datetime.now(datetime.timezone.utc),
                train_number=train_number,
                train_name=config["name"],
                train_class=config["class"]
            ))
            
        return options
