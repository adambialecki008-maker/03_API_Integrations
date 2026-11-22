from api_integrations.alarms_analysis.models import (
    AlarmNoteAnalysis,
    AlarmAnalysisResult,
    EvaluationStats,
    EvaluationCaseResult,
)
import pytest


@pytest.fixture
def valid_alarm_note():
    return AlarmNoteAnalysis(
        category="electrical",
        priority="high",
        summary="Test sumamry",
        evidence=["ev_1", "ev_2", "ev_3"],
        requires_review=False,
    )


@pytest.fixture
def valid_analysis_result():
    return AlarmAnalysisResult(
        category="electrical",
        priority="low",
        requires_review=False,
    )


@pytest.fixture
def valid_evaluation_case(valid_analysis_result):
    return EvaluationCaseResult(
        id="PLC_01",
        expected=valid_analysis_result,
        actual=valid_analysis_result,
    )


@pytest.fixture
def valid_evaluation_stats(valid_evaluation_case):
    return EvaluationStats(
        llm_model="qwen2.5:3b",
        category_accuracy=1.0,
        priority_accuracy=1.0,
        requires_review_accuracy=1.0,
        exact_match=1,
        results=[valid_evaluation_case],
        total_attempts=1,
        failed_model=0,
        failed_evidence=0,
    )
