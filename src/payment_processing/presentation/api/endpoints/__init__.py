from __future__ import annotations

from typing import TYPE_CHECKING

from payment_processing.presentation.api.endpoints.healthcheck.routers import (
    router as healthcheck_router,
)
from payment_processing.presentation.api.endpoints.payments.routers import (
    router as payments_router,
)

if TYPE_CHECKING:
    from fastapi import APIRouter

ROUTERS: tuple[APIRouter, ...] = (
    payments_router,
    healthcheck_router,
)
