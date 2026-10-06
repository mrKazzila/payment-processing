from contextlib import AbstractAsyncContextManager
from typing import Protocol


class TransactionManager(Protocol):
    def begin(self) -> AbstractAsyncContextManager[None]: ...
