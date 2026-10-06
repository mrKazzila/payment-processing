from collections.abc import AsyncIterator
from contextlib import AbstractAsyncContextManager, asynccontextmanager
from dataclasses import dataclass
from typing import final

from sqlalchemy.ext.asyncio import AsyncSession


@final
@dataclass(slots=True, frozen=True)
class SQLAlchemyTransactionManager:
    session: AsyncSession

    def begin(self) -> AbstractAsyncContextManager[None]:
        return self._begin()

    @asynccontextmanager
    async def _begin(self) -> AsyncIterator[None]:
        async with self.session.begin():
            yield
