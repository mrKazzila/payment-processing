import httpx


def create_webhook_client() -> httpx.AsyncClient:
    return httpx.AsyncClient(
        timeout=httpx.Timeout(
            timeout=5.0,
            connect=3.0,
        ),
        follow_redirects=False,
    )
