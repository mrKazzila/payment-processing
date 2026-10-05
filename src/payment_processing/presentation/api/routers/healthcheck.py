from fastapi import APIRouter

from payment_processing.presentation.api.schemas.health import (
    SHealthcheckResponse,
)

router = APIRouter(tags=["Health"])


@router.get("/health")
async def healthcheck() -> SHealthcheckResponse:
    return SHealthcheckResponse(
        status="OK",
    )
