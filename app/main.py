from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.logic_engine import (
    calculate_runtime_minutes,
    is_critical_event,
    is_maintenance_ping,
)
from app.logger_config import logger
from app.notifier import send_notification
from app.schemas import GeneratorPayload

app = FastAPI(title="Kilowatt Kinetic Middleware")


def _clean_errors(errors: list[dict]) -> list[dict]:
    for error in errors:
        ctx = error.get("ctx")
        if ctx:
            for key, value in ctx.items():
                if isinstance(value, Exception):
                    ctx[key] = str(value)
    return errors


@app.exception_handler(RequestValidationError)
async def validation_error_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """Log and return a structured 422 response for malformed payloads.

    FastAPI's default validation handler is silent. This override ensures every
    rejected payload is written to the application log before the error is
    returned to the caller.

    Args:
        request: The incoming HTTP request that failed validation.
        exc: Pydantic validation error containing per-field failure details.

    Returns:
        JSONResponse with HTTP 422 and a list of field-level error descriptors.
    """
    errors = _clean_errors(exc.errors())
    logger.error("Malformed payload from %s: %s", request.client.host, errors)
    return JSONResponse(status_code=422, content={"detail": errors})


@app.post("/webhook/generator")
def process_generator_webhook(payload: GeneratorPayload) -> dict:
    """Ingest a VoltPulse generator telemetry webhook and route it accordingly.

    Processing pipeline:
      1. Discard ROUTINE_TEST pings silently.
      2. Calculate estimated runtime from fuel level and current load.
      3. Forward CRITICAL_PHASE_LOSS or low-fuel (<15 %) events to the
         field technician notification endpoint.
      4. Return the processed telemetry summary to the caller.

    Args:
        payload: Validated GeneratorPayload parsed from the request body.

    Returns:
        Dict containing a status message and the processed telemetry data.

    Raises:
        HTTPException: HTTP 500 if the downstream notification call fails.
    """
    logger.info("Received payload: %s", payload.model_dump())

    if is_maintenance_ping(payload.status_code):
        logger.info("ROUTINE_TEST discarded.")
        return {"message": "Routine maintenance ignored"}

    runtime_minutes = calculate_runtime_minutes(
        payload.fuel_level,
        payload.amperage,
    )

    response_data = {
        "status_code": payload.status_code,
        "fuel_level": payload.fuel_level,
        "estimated_runtime_minutes": runtime_minutes,
    }

    if is_critical_event(payload.status_code, payload.fuel_level):
        try:
            send_notification(response_data)
            logger.info("Critical notification sent for status: %s", payload.status_code)
        except Exception as error:
            logger.error("Notification failed: %s", error)
            raise HTTPException(status_code=500, detail="Notification failed") from error

    return {"message": "Webhook processed", "data": response_data}