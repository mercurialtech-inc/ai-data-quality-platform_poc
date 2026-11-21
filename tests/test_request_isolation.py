
import asyncio
import uuid
from concurrent.futures import ThreadPoolExecutor

from fastapi.testclient import TestClient

from api import app
from request_context import request_id_var


# Temporary endpoint to inspect the active context.
@app.get("/test/context")
async def inspect_context():
    request_id_before = request_id_var.get()

    # Allow other requests to execute concurrently.
    await asyncio.sleep(0.05)

    request_id_after = request_id_var.get()

    return {
        "before": request_id_before,
        "after": request_id_after,
    }


# Temporary endpoint that raises an exception.
@app.get("/test/context-error")
async def context_error():
    raise RuntimeError("Simulated failure")


def test_concurrent_request_isolation():
    def send_request():
        with TestClient(app) as client:
            return client.get("/test/context")

    with ThreadPoolExecutor(max_workers=5) as executor:
        responses = list(executor.map(
            lambda _: send_request(),
            range(5)
        ))

    request_ids = []

    for response in responses:
        assert response.status_code == 200

        data = response.json()
        header_id = response.headers["X-Request-ID"]

        # The context remains stable during the request.
        assert data["before"] == data["after"]

        # The context matches the response header.
        assert data["before"] == header_id

        # The ID is a valid UUID.
        assert str(uuid.UUID(header_id)) == header_id

        request_ids.append(header_id)

    # All five requests must have different IDs.
    assert len(set(request_ids)) == 5


def test_context_cleanup_after_exception():
    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.get("/test/context-error")

    assert response.status_code == 500

    # No context should remain in the test's execution context.
    assert request_id_var.get() is None
