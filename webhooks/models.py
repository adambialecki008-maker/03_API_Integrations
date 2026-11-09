from pydantic import BaseModel, Field, field_validator
from typing import Literal


class AlarmData(BaseModel):
    machine: str
    alarm_code: int = Field(strict=True)

    @field_validator("machine")
    @classmethod
    def validate_machine(cls, value: str) -> str:
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Invalid machine")
        return value.strip()


class WebhookPayload(BaseModel):
    event_id: str = Field(min_length=1, pattern=r"\S")
    event: Literal["alarm.created"]
    data: AlarmData
