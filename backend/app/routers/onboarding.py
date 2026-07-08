from fastapi import APIRouter, Depends

from app.dependencies.auth import get_current_user

from app.schemas.onboarding import (
    OnboardingRequest,
)

from app.services.onboarding_service import (
    OnboardingService,
)

router = APIRouter(
    prefix="/onboarding",
    tags=["Onboarding"],
)


@router.get("/status")
def onboarding_status(
    current_user=Depends(get_current_user),
):

    return OnboardingService.status(
        current_user.id,
    )


@router.post("")
def submit_onboarding(
    data: OnboardingRequest,
    current_user=Depends(get_current_user),
):

    return OnboardingService.submit(
        current_user.id,
        data.model_dump(),
    )