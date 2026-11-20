from pydantic import BaseModel, Field
from typing import Literal


class AlarmNoteAnalysis(BaseModel):
    category: Literal["electrical", "mechanical", "process", "unknown"]
    priority: Literal["high", "medium", "low", "unknown"]
    summary: str = Field(min_length=1, max_length=200, pattern=r"\S")
    evidence: list[str] = Field(max_length=3)
    requires_review: bool = Field(strict=True)


class AlarmNoteRequest(BaseModel):
    note: str = Field(min_length=1)
