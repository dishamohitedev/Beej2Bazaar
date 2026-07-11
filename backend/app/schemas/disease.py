from pydantic import BaseModel
from typing import List, Optional


class DiseaseDetectionResponse(BaseModel):
    report_id: str
    disease_name: str
    confidence: float
    severity: str
    recommendation: List[str]
    consult_expert: bool


class DiseaseReport(BaseModel):
    id: str
    disease_name: str
    confidence: float
    status: str
    image_url: Optional[str] = None
    created_at: str


class DiseaseReportDetail(BaseModel):
    id: str
    disease_name: str
    confidence: float
    image_url: Optional[str] = None
    ai_response: dict
    status: str
    created_at: str