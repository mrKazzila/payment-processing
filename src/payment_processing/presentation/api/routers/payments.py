from fastapi import APIRouter

router = APIRouter(tags=["Payments"])


@router.post("/api/v1/payments")
async def create_paymant():
    return "create_paymant"


@router.get("/api/v1/payments/{payment_id}")
async def get_payment(payment_id: int):
    return f"get_payment_{payment_id}"
