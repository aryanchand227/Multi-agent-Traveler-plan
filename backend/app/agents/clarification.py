from typing import Dict, Any
from app.agents.base import BaseAgent
from app.graph.state import TravelState

class ClarificationAgent(BaseAgent):
    def __init__(self, llm_provider):
        super().__init__(llm_provider=llm_provider)

    @property
    def name(self) -> str:
        return "ClarificationAgent"

    async def run(self, state: TravelState) -> Dict[str, Any]:
        missing_fields = []
        
        if not state.get("origin"):
            missing_fields.append({"field": "origin", "question": "Where will you be departing from?"})
            
        has_duration = state.get("duration_days") is not None
        has_dates = state.get("departure_date") is not None and state.get("return_date") is not None
        
        if not (has_duration or has_dates):
            missing_fields.append({
                "field": "duration_days", 
                "question": "When are you planning to travel, or how many days will the trip be?"
            })
            
        if not state.get("travelers"):
            missing_fields.append({
                "field": "travelers", 
                "question": "How many people will be traveling?"
            })
            
        if missing_fields:
            return {
                "requires_clarification": True,
                "clarification_questions": missing_fields
            }
        else:
            return {
                "requires_clarification": False,
                "is_valid_requirements": True
            }
