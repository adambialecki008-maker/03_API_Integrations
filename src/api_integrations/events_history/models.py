from api_integrations.webhooks.models import AlarmData
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Annotated, Literal
from pydantic import BeforeValidator, BaseModel, Field, model_validator


def parse_utc_iso(value: str | None) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError("Timestamp must be a string")
    dt = datetime.fromisoformat(value)
    if dt.tzinfo is None:
        raise ValueError("No timezone provided")
    return dt.astimezone(ZoneInfo("UTC")).isoformat()


TimestampUTC = Annotated[str, BeforeValidator(parse_utc_iso)]


class RegisteredEvent(BaseModel):
    event_id: str = Field(min_length=1, pattern=r"\S")
    event: Literal["alarm.created"]
    data: AlarmData
    timestamp: TimestampUTC
    received_at: TimestampUTC


class EventsHistoryRequest(BaseModel):
    event_id: str | None = None
    machine: str | None = None
    time_from: TimestampUTC | None = None
    time_to: TimestampUTC | None = None
    limit: int | None = Field(ge=1, le=100, default=100)
    offset: int | None = Field(ge=0, default=0)

    @model_validator(mode="after")
    def check_time_range(self) -> "EventsHistoryRequest":
        if self.time_from is not None and self.time_to is not None:
            if self.time_from > self.time_to:
                raise ValueError("time_from must be earlier than or equal to time_to")
        return self
