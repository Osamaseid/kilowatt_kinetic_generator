from pydantic import BaseModel, Field, field_validator


class GeneratorPayload(BaseModel):
    """Validated telemetry payload from the VoltPulse API webhook."""

    voltage: float = Field(gt=0, description="Line voltage in volts (must be positive).")
    amperage: float = Field(ge=0, description="Current load in amps (zero-load is valid).")
    fuel_level: float = Field(ge=0, le=100, description="Remaining fuel as a percentage (0–100).")
    status_code: str = Field(description="VoltPulse status code, e.g. NORMAL_OPERATION.")

    @field_validator("status_code")
    @classmethod
    def status_code_must_not_be_blank(cls, value: str) -> str:
        """Reject empty or whitespace-only status codes."""
        if not value.strip():
            raise ValueError("status_code must not be blank.")
        return value.strip().upper()