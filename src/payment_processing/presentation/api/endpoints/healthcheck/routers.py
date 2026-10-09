from fastapi import APIRouter

from payment_processing.presentation.api.endpoints.healthcheck.schemas import (
    SHealthcheckResponse,
)

router = APIRouter(tags=["Health"])


@router.get("/health")
async def healthcheck() -> SHealthcheckResponse:
    return SHealthcheckResponse(
        status="OK",
    )
