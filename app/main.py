from time import perf_counter
from uuid import uuid4

from fastapi import FastAPI
from fastapi import Request
from fastapi.responses import JSONResponse

from app.api.routes.health import router as health_router
from app.core.logging import get_logger
from app.core.logging import request_id_context
from app.core.logging import setup_logging

setup_logging()
logger = get_logger(__name__)

app = FastAPI(
    title='LLM Evaluation Platform',
    version='0.1.0',
)


@app.middleware('http')
async def request_logging_middleware(request: Request, call_next):
    request_id = request.headers.get('X-Request-ID', str(uuid4()))
    token = request_id_context.set(request_id)
    start_time = perf_counter()

    try:
        response = await call_next(request)
        duration_ms = round((perf_counter() - start_time) * 1000, 2)
        response.headers['X-Request-ID'] = request_id

        logger.info(
            'request_completed method=%s path=%s status_code=%s duration_ms=%s',
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
        )

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


app.include_router(health_router)
