from faststream.specification import AsyncAPI, Contact

WORKER_DESCRIPTION = """
# Сервис обработки платежей

Consumer очереди `payments.new`.

## Назначение
- Валидация входящих событий.
- Обработка платежа через эмуляцию платёжного шлюза.
- Сохранение результата обработки.
- Отправка webhook с повторными попытками.

## Ошибки
Некорректные сообщения направляются в DLQ.
Временные ошибки обрабатываются повторно;
после исчерпания попыток сообщение направляется в DLQ.
"""


def create_specification(
    *,
    title: str,
    version: str,
) -> AsyncAPI:
    return AsyncAPI(
        title=title,
        version=version,
        description=WORKER_DESCRIPTION,
        contact=Contact(name="mrKazzila"),
        schema_version="3.0.0",
    )
