from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from app.agents.base import BaseAgent
from app.graph.state import TravelState

class IntakeExtraction(BaseModel):
    origin: Optional[str] = Field(default=None, description="Origin city or airport")
    destination: Optional[str] = Field(default=None, description="Destination city or airport")
    departure_date: Optional[str] = Field(default=None, description="Departure date (YYYY-MM-DD)")
    return_date: Optional[str] = Field(default=None, description="Return date (YYYY-MM-DD)")
    duration_days: Optional[int] = Field(default=None, description="Duration of trip in days")
    budget: Optional[float] = Field(default=None, description="Budget amount")
    currency: Optional[str] = Field(default=None, description="Currency")
    travelers: Optional[int] = Field(default=None, description="Number of travelers")
    travel_style: Optional[str] = Field(default=None, description="Travel style (e.g., budget, standard, premium, luxury)")
    preferred_transport: Optional[List[str]] = Field(default=None, description="List of preferred transport modes")
    interests: Optional[List[str]] = Field(default=None, description="List of interests")
    special_requirements: Optional[List[str]] = Field(default=None, description="Any special requirements")

class IntakeAgent(BaseAgent):
    def __init__(self, llm_provider):
        super().__init__(llm_provider=llm_provider)

    @property
    def name(self) -> str:
        return "IntakeAgent"

    async def run(self, state: TravelState) -> Dict[str, Any]:
        system_prompt = "Extract travel details from the user's request. Also apply any clarification answers provided. Be precise."
        user_prompt = f"Request: {state.get('raw_user_request', '')}\nClarifications: {state.get('clarification_answers', {})}"
        
        result = await self.get_structured_response(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            response_model=IntakeExtraction
        )
        
        updates = {}
        for field, value in result.model_dump().items():
            if value is not None:
                updates[field] = value
                
        return updates
