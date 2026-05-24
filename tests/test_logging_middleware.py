from time import perf_counter
from uuid import uuid4

from fastapi import FastAPI
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient

from app.core.logging import get_logger
from app.core.logging import request_id_context
from app.main import app

logger = get_logger(__name__)


async def test_request_logging_middleware(request: Request, call_next):
    request_id = request.headers.get('X-Request-ID', str(uuid4()))
    token = request_id_context.set(request_id)
    start_time = perf_counter()

    try:
        response = await call_next(request)
        response.headers['X-Request-ID'] = request_id
        return response
    except Exception:
        duration_ms = round((perf_counter() - start_time) * 1000, 2)
        logger.exception(
            'request_failed method=%s path=%s duration_ms=%s',
            request.method,
            request.url.path,
            duration_ms,
        )
        return JSONResponse(
            status_code=500,
            content={
                'detail': 'Internal server error',
                'request_id': request_id,
            },
            headers={'X-Request-ID': request_id},
        )
    finally:
        request_id_context.reset(token)



def test_request_id_header_is_returned() -> None:
    client = TestClient(app)

    response = client.get('/health', headers={'X-Request-ID': 'test-request-id'})

    assert response.status_code == 200
    assert response.headers['X-Request-ID'] == 'test-request-id'



def test_request_id_header_is_returned_on_server_error() -> None:
    test_app = FastAPI()
    test_app.middleware('http')(test_request_logging_middleware)

    @test_app.get('/error')
    def raise_test_error():
        raise RuntimeError('test error')

    client = TestClient(test_app, raise_server_exceptions=False)

    response = client.get('/error', headers={'X-Request-ID': 'error-request-id'})

    assert response.status_code == 500
    assert response.headers['X-Request-ID'] == 'error-request-id'
    assert response.json()['request_id'] == 'error-request-id'
