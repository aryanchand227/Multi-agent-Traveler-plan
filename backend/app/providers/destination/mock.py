"""Mock destination provider."""
from __future__ import annotations

import datetime
import uuid

from app.providers.destination.base import DestinationProvider
from app.schemas.activities import ActivityOption, ActivityCategory
from app.schemas.transport import SourceType


class MockDestinationProvider(DestinationProvider):
    """Mock implementation of DestinationProvider."""

    async def search_activities(
        self,
        destination: str,
        interests: list[str] | None = None,
        travel_style: str = "standard",
        days: int = 1,
    ) -> list[ActivityOption]:
        """Search for activities at a destination."""
        dest_lower = destination.lower()
        options = []
        
        # Hardcoded mocks for some Indian cities
        activities_map = {
            "goa": [
                ("Baga Beach Visit", ActivityCategory.RELAXATION, "North Goa", "Enjoy the lively atmosphere and shacks at Baga Beach", 180, 0),
                ("Calangute Beach Watersports", ActivityCategory.ADVENTURE, "North Goa", "Parasailing and jet skiing at Calangute", 120, 1500),
                ("Palolem Beach Sunset", ActivityCategory.RELAXATION, "South Goa", "Quiet and scenic beach sunset", 120, 0),
                ("Old Goa Churches Tour", ActivityCategory.HISTORICAL, "Old Goa", "Visit Basilica of Bom Jesus and Se Cathedral", 180, 200),
                ("Spice Plantation Tour", ActivityCategory.NATURE, "Ponda", "Guided tour of tropical spice plantation with traditional lunch", 240, 800),
                ("Anjuna Flea Market", ActivityCategory.SHOPPING, "Anjuna", "Shopping for souvenirs and local crafts", 180, 500),
                ("Dudhsagar Falls Trek", ActivityCategory.ADVENTURE, "Sanguem", "Jeep safari and trek to the magnificent waterfalls", 360, 2000),
                ("Mandovi River Cruise", ActivityCategory.RELAXATION, "Panaji", "Evening sunset cruise with music and dancing", 120, 600)
            ],
            "delhi": [
                ("Red Fort Exploration", ActivityCategory.HISTORICAL, "Old Delhi", "Explore the iconic 17th-century Mughal fortress", 180, 500),
                ("Qutub Minar Visit", ActivityCategory.HISTORICAL, "Mehrauli", "See the tallest brick minaret in the world", 120, 500),
                ("India Gate Evening Walk", ActivityCategory.RELAXATION, "Rajpath", "Stroll around the war memorial in the evening", 60, 0),
                ("Chandni Chowk Food Walk", ActivityCategory.FOOD, "Old Delhi", "Taste authentic street food like parathas and jalebis", 180, 800),
                ("Hauz Khas Village Nightlife", ActivityCategory.NIGHTLIFE, "Hauz Khas", "Enjoy bars and cafes in this trendy neighborhood", 240, 2000),
                ("Lotus Temple Visit", ActivityCategory.CULTURAL, "Kalkaji", "Experience peace at the Bahai House of Worship", 90, 0),
                ("Dilli Haat Shopping", ActivityCategory.SHOPPING, "INA", "Buy traditional handicrafts and handlooms from across India", 150, 1000),
                ("Humayun's Tomb Tour", ActivityCategory.HISTORICAL, "Nizamuddin", "Visit the beautiful Mughal garden tomb", 120, 500)
            ],
            "mumbai": [
                ("Gateway of India", ActivityCategory.HISTORICAL, "Colaba", "Visit the iconic arch monument overlooking the Arabian Sea", 60, 0),
                ("Marine Drive Sunset", ActivityCategory.RELAXATION, "South Mumbai", "Walk along the Queen's Necklace at sunset", 90, 0),
                ("Elephanta Caves Tour", ActivityCategory.HISTORICAL, "Elephanta Island", "Ferry ride and tour of ancient rock-cut caves", 240, 1000),
                ("Colaba Causeway Shopping", ActivityCategory.SHOPPING, "Colaba", "Street shopping for clothes, jewelry, and antiques", 120, 1500),
                ("Juhu Beach Street Food", ActivityCategory.FOOD, "Juhu", "Try pav bhaji and bhel puri by the beach", 120, 400),
                ("Bollywood Studio Tour", ActivityCategory.CULTURAL, "Goregaon", "Behind the scenes look at Indian cinema", 300, 2500),
                ("Siddhivinayak Temple", ActivityCategory.CULTURAL, "Prabhadevi", "Visit one of Mumbai's most famous temples", 60, 0),
                ("Bandra Fort and Bandstand", ActivityCategory.RELAXATION, "Bandra", "View the sea link and explore the fort ruins", 90, 0)
            ]
        }
        
        # Generic fallback
        generic_activities = [
            ("City Center Walking Tour", ActivityCategory.CULTURAL, "Downtown", "Guided walk through the main attractions", 120, 500),
            ("Local Museum Visit", ActivityCategory.HISTORICAL, "City Center", "Learn about local history and culture", 180, 300),
            ("Botanical Gardens", ActivityCategory.NATURE, "Suburbs", "Relaxing walk through beautiful gardens", 120, 100),
            ("Shopping District Visit", ActivityCategory.SHOPPING, "Downtown", "Explore local shops and boutiques", 180, 1000),
            ("Food Tasting Tour", ActivityCategory.FOOD, "Various", "Sample popular local dishes", 150, 1200),
            ("Viewpoint Hike", ActivityCategory.ADVENTURE, "Outskirts", "Short hike for a panoramic view", 240, 0),
            ("Evening Entertainment", ActivityCategory.NIGHTLIFE, "Downtown", "Local cultural show or live music", 180, 800),
            ("Relaxation Spa", ActivityCategory.RELAXATION, "City Center", "Traditional massage and spa treatment", 120, 2000)
        ]
        
        acts_to_use = generic_activities
        for city in activities_map:
            if city in dest_lower:
                acts_to_use = activities_map[city]
                break
                
        now = datetime.datetime.now(datetime.timezone.utc)
        
        for act in acts_to_use:
            options.append(
                ActivityOption(
                    id=str(uuid.uuid4()),
                    name=act[0],
                    category=act[1],
                    location=act[2],
                    description=act[3],
                    estimated_duration_minutes=act[4],
                    estimated_cost=act[5],
                    best_time="Morning" if act[1] in [ActivityCategory.NATURE, ActivityCategory.ADVENTURE] else "Anytime",
                    weather_dependency=act[1] in [ActivityCategory.NATURE, ActivityCategory.ADVENTURE, ActivityCategory.RELAXATION],
                    source="MockDestinationAPI",
                    source_type=SourceType.MOCK,
                    retrieved_at=now
                )
            )
            
        return options

    def get_provider_name(self) -> str:
        return "Mock Destination Provider"
