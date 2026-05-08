from app.config import GENERATOR_CAPACITY

CRITICAL_CODES = {"CRITICAL_PHASE_LOSS"}
LOW_FUEL_THRESHOLD = 15.0


def calculate_runtime_minutes(
    fuel_percentage: float,
    current_load: float,
) -> float:
    """Estimate remaining runtime in minutes.

    Formula: ((fuel_percentage * GENERATOR_CAPACITY) / (current_load * 0.85)) * 60

    The inner division yields runtime in hours; multiplying by 60 converts to
    minutes. A load of zero means the generator is idle, so runtime is undefined
    and returned as 0.

    Args:
        fuel_percentage: Remaining fuel expressed as a percentage (0–100).
        current_load: Active electrical load in amps.

    Returns:
        Estimated runtime in minutes, rounded to two decimal places.
    """
    if current_load <= 0:
        return 0.0

    runtime_hours = (fuel_percentage * GENERATOR_CAPACITY) / (current_load * 0.85)
    return round(runtime_hours * 60, 2)


def is_critical_event(status_code: str, fuel_level: float) -> bool:
    """Determine whether a telemetry event requires immediate escalation.

    An event is critical when the VoltPulse status code signals a hardware
    fault (e.g. CRITICAL_PHASE_LOSS) or when remaining fuel drops below
    the LOW_FUEL_THRESHOLD (15 %), whichever occurs first.

    Args:
        status_code: Normalised VoltPulse status code from the payload.
        fuel_level: Remaining fuel as a percentage (0–100).

    Returns:
        True if the event must be routed to the field technician endpoint.
    """
    return status_code in CRITICAL_CODES or fuel_level < LOW_FUEL_THRESHOLD


def is_maintenance_ping(status_code: str) -> bool:
    """Identify routine scheduled-test pings that should be silently discarded.

    The VoltPulse platform emits ROUTINE_TEST signals during scheduled
    self-checks. These carry no actionable information and must not trigger
    notifications or runtime calculations.

    Args:
        status_code: Normalised VoltPulse status code from the payload.

    Returns:
        True if the payload is a routine maintenance ping.
    """
    return status_code == "ROUTINE_TEST"