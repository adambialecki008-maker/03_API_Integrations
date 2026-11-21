from pydantic import BaseModel, Field, ConfigDict
from typing import Literal

categories = Literal["electrical", "mechanical", "process", "unknown"]
priorities = Literal["high", "medium", "low", "unknown"]


class AlarmNoteAnalysis(BaseModel):
    category: categories
    priority: Literal["high", "medium", "low", "unknown"]
    summary: str = Field(min_length=1, max_length=200, pattern=r"\S")
    evidence: list[str] = Field(max_length=3)
    requires_review: bool = Field(strict=True)
    model_config = ConfigDict(extra="forbid")


class AlarmNoteRequest(BaseModel):
    note: str = Field(min_length=1)


class AlarmAnalysisResult(BaseModel):
    id: str = Field(min_length=1, pattern=r"\S")
    category: categories
    priority: priorities
    requires_review: bool = Field(strict=True)


class EvaluationStats(BaseModel):
    llm_model: str = Field(min_length=1, pattern=r"\S")
    cattegory_accuracy: float
    priority_accuracy: float
    requires_review_accuracy: float
    exact_match: int
    expected_results: list[AlarmAnalysisResult]
    actual_results: list[AlarmAnalysisResult]
