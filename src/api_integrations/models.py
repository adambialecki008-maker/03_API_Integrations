from pydantic import (
    BaseModel,
    Field,
    field_validator,
    StrictStr,
    BeforeValidator,
    model_validator,
)
from typing import Literal, Annotated
from datetime import datetime
from zoneinfo import ZoneInfo


class AlarmData(BaseModel):
    machine: str
    alarm_code: int = Field(strict=True)

    @field_validator("machine")
    @classmethod
    def validate_machine(cls, value: str) -> str:
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Invalid machine")
        return value.strip()


def parse_utc_iso(value: str | None) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError("Timestamp must be a string")
    dt = datetime.fromisoformat(value)
    if dt.tzinfo is None:
        raise ValueError("No timezone provided")
    return dt.astimezone(ZoneInfo("UTC")).isoformat()


Time_Registered = Annotated[str, BeforeValidator(parse_utc_iso)]
Time_Requested = Annotated[str | None, BeforeValidator(parse_utc_iso)]


class WebhookPayload(BaseModel):
    event_id: str = Field(min_length=1, pattern=r"\S")
    event: Literal["alarm.created"]
    timestamp: int = Field(strict=True)
    data: AlarmData


class RegisteredEvent(BaseModel):
    event_id: str = Field(min_length=1, pattern=r"\S")
    event: Literal["alarm.created"]
    data: AlarmData
    timestamp: Time_Registered
    received_at: Time_Registered


class EventsHistoryRequest(BaseModel):
    event_id: str | None = None
    machine: str | None = None
    time_from: Time_Requested
    time_to: Time_Requested
    limit: int | None = Field(ge=1, le=100, default=100)

    @model_validator(mode="after")
    def check_time_range(self) -> "EventsHistoryRequest":
        if self.time_from is not None and self.time_to is not None:
            if self.time_from > self.time_to:
                raise ValueError("time_from must be earlier than or equal to time_to")
        return self
