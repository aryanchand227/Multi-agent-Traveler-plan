from typing import Any
from app.agents.base import BaseAgent
from app.graph.state import TravelState
from app.agents.bus import BusAgent
from app.agents.train import TrainAgent
from app.agents.flight import FlightAgent
from app.services.transport_ranker import rank_transport_options
from app.providers.transport.base import BusProvider, TrainProvider, FlightProvider

class TransportSupervisor(BaseAgent):
    def __init__(self, llm_provider, bus_provider: BusProvider, train_provider: TrainProvider, flight_provider: FlightProvider):
        super().__init__(llm_provider)
        self.bus_agent = BusAgent(llm_provider, bus_provider)
        self.train_agent = TrainAgent(llm_provider, train_provider)
        self.flight_agent = FlightAgent(llm_provider, flight_provider)

    @property
    def name(self) -> str:
        return "TransportSupervisor"

    async def run(self, state: TravelState) -> dict[str, Any]:
        bus_res = await self.bus_agent.run(state)
        train_res = await self.train_agent.run(state)
        flight_res = await self.flight_agent.run(state)
        
        all_options = []
        all_options.extend(bus_res.get("transport_options", []))
        all_options.extend(train_res.get("transport_options", []))
        all_options.extend(flight_res.get("transport_options", []))
        
        travel_style = str(state.get("travel_style", "standard")).lower()
        preferred_transport = state.get("preferred_transport", [])
        
        ranked_options = rank_transport_options(all_options, travel_style, preferred_transport)
        
        selected = ranked_options[0] if ranked_options else None
        
        return {
            "transport_options": ranked_options,
            "selected_transport": selected
        }
