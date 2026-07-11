from typing import List

from fastapi import APIRouter, Depends, File, UploadFile

from app.dependencies.auth import get_current_user
from app.schemas.disease import (
    DiseaseDetectionResponse,
    DiseaseReport,
    DiseaseReportDetail,
)
from app.services.disease_service import DiseaseService

router = APIRouter(prefix="/disease", tags=["Disease"])


@router.post(
    "/detect",
    response_model=DiseaseDetectionResponse,
)
async def detect_disease(
    image: UploadFile = File(...),
    current_user=Depends(get_current_user),
):
    return await DiseaseService.detect(
        current_user.id,
        image,
    )


@router.get(
    "/history",
    response_model=List[DiseaseReport],
)
def get_history(
    current_user=Depends(get_current_user),
):
    return DiseaseService.get_history(
        current_user.id,
    )


@router.get(
    "/{report_id}",
    response_model=DiseaseReportDetail
)
def get_report(
    report_id: str,
    current_user=Depends(get_current_user),
):
    return DiseaseService.get_report(
        current_user.id,
        report_id,
    )