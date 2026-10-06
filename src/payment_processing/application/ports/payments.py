from typing import Protocol
from uuid import UUID

from payment_processing.domain.payment import Payment


class PaymentRepository(Protocol):
    async def get_by_id(self, *, payment_id: UUID) -> Payment | None: ...

    async def get_by_idempotency_key(
        self,
        *,
        idempotency_key: str,
    ) -> Payment | None: ...

    async def add(self, *, payment: Payment) -> None: ...

    async def get_by_id_for_update(
        self,
        *,
        payment_id: UUID,
    ) -> Payment | None: ...

    async def update(self, *, payment: Payment) -> None: ...
