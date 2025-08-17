from pydantic import BaseModel
from typing import Optional, List

class LegalQueryRequest(BaseModel):
    query: str
    language: Optional[str] = "en"
    query_type: Optional[str] = "general"  # "constitution", "scenario", "general"
    document_id: Optional[int] = None # Added this line

class LegalQueryResponse(BaseModel):
    response: str
    sources: List[str]
    related_sections: List[str]
    confidence: float
    language: str

class ScenarioRequest(BaseModel):
    scenario_type: str
    description: Optional[str] = None
    language: Optional[str] = "en"

class ConstitutionQueryRequest(BaseModel):
    article_or_term: str
    language: Optional[str] = "en"