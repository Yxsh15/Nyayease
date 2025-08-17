from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class DocumentUpload(BaseModel):
    filename: str
    content_type: str

class DocumentResponse(BaseModel):
    id: int
    filename: str
    extracted_text: str
    analysis_result: str
    upload_date: datetime
    
    class Config:
        from_attributes = True

class DocumentAnalysisRequest(BaseModel):
    document_id: int
    language: Optional[str] = "en"