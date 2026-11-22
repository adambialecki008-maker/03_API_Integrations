from pydantic import BaseModel, Field, ConfigDict, model_validator
from typing import Literal

CategoriesType = Literal["electrical", "mechanical", "process", "unknown"]
PrioritiesType = Literal["high", "medium", "low", "unknown"]
ErrorType = Literal[
    "timeout",
    "connection",
    "invalid_json",
    "invalid_schema",
    "invalid_evidence",
    "model_error",
]


class AlarmNoteAnalysis(BaseModel):
    category: CategoriesType
    priority: PrioritiesType
    summary: str = Field(min_length=1, max_length=200, pattern=r"\S")
    evidence: list[str] = Field(max_length=3)
    requires_review: bool = Field(strict=True)
    model_config = ConfigDict(extra="forbid")


class AlarmNoteRequest(BaseModel):
    note: str = Field(min_length=1)


class AlarmAnalysisResult(BaseModel):
    category: CategoriesType
    priority: PrioritiesType
    requires_review: bool = Field(strict=True)
    model_config = ConfigDict(extra="forbid")


class EvaluationCaseResult(BaseModel):
    id: str = Field(min_length=1, pattern=r"\S", strict=True)
    expected: AlarmAnalysisResult
    actual: AlarmAnalysisResult | None = None
    error_type: ErrorType | None = None
    error_message: str | None = None
    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="after")
    def validate_result(self):
        if (self.actual is None) == (self.error_type is None):
            raise ValueError("Exactly one of actual or error_type must be provided")
        return self


class EvaluationStats(BaseModel):
    llm_model: str = Field(min_length=1, pattern=r"\S")
    category_accuracy: float = Field(strict=True, ge=0, le=1.0)
    priority_accuracy: float = Field(strict=True, ge=0, le=1.0)
    requires_review_accuracy: float = Field(strict=True, ge=0, le=1.0)
    exact_match: int = Field(strict=True, ge=0)
    results: list[EvaluationCaseResult]
    total_attempts: int = Field(strict=True, ge=0)
    failed_model: int = Field(strict=True, ge=0)
    failed_evidence: int = Field(strict=True, ge=0)
    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="after")
    def validate_statistics(self):
        if self.total_attempts != len(self.results):
            raise ValueError("total_attempts must equal the number of results")
        if self.exact_match > self.total_attempts:
            raise ValueError("exact_match cannot exceed total_attempts")
        return self
