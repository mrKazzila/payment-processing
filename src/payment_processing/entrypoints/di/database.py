from collections.abc import AsyncIterator

from dishka import Provider, Scope, from_context, provide
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
)

from payment_processing.application.ports.outbox import OutboxRepository
from payment_processing.application.ports.payments import PaymentRepository
from payment_processing.application.ports.transactions import (
    TransactionManager,
)
from payment_processing.config.settings import Settings
from payment_processing.infrastructure.database.engine import (
    create_database_engine,
    create_database_url,
)
from payment_processing.infrastructure.database.repositories.outbox import (
    SQLAlchemyOutboxRepository,
)
from payment_processing.infrastructure.database.repositories.payments import (
    SQLAlchemyPaymentRepository,
)
from payment_processing.infrastructure.database.session import (
    create_session_factory,
)
from payment_processing.infrastructure.database.transactions import (
    SQLAlchemyTransactionManager,
)


class RepositoryProvider(Provider):
    scope = Scope.REQUEST

    payments = provide(
        SQLAlchemyPaymentRepository,
        provides=PaymentRepository,
    )
    outbox = provide(
        SQLAlchemyOutboxRepository,
        provides=OutboxRepository,
    )
    transactions = provide(
        SQLAlchemyTransactionManager,
        provides=TransactionManager,
    )


class DatabaseProvider(Provider):
    settings = from_context(
        provides=Settings,
        scope=Scope.APP,
    )

    @provide(scope=Scope.APP)
    async def engine(
        self,
        settings: Settings,
    ) -> AsyncIterator[AsyncEngine]:
        database = settings.database
        engine = create_database_engine(
            url=create_database_url(
                user=database.user,
                password=database.password.get_secret_value(),
                host=database.host,
                port=database.port,
                name=database.name,
            ),
            pool_size=database.pool_size,
            max_overflow=database.max_overflow,
            pool_timeout=database.pool_timeout,
        )
        try:
            yield engine
        finally:
            await engine.dispose()

    @provide(scope=Scope.APP)
    def session_factory(
        self,
        engine: AsyncEngine,
    ) -> async_sessionmaker[AsyncSession]:
        return create_session_factory(engine=engine)

    @provide(scope=Scope.REQUEST)
    async def session(
        self,
        session_factory: async_sessionmaker[AsyncSession],
    ) -> AsyncIterator[AsyncSession]:
        async with session_factory() as session:
            yield session
