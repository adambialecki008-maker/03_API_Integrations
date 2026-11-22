from api_integrations.alarms_analysis.models import (
    AlarmAnalysisResult,
    EvaluationCaseResult,
    EvaluationStats,
)
from pydantic import ValidationError
import pytest


################### Alarm Analysis Result ########################################################
@pytest.mark.parametrize("param", ["test", 123, None, False, " "])
def test_alarm_analysis_result_raises_on_invalid_category(valid_analysis_result, param):
    raw_data = valid_analysis_result.model_dump()
    raw_data["category"] = param
    with pytest.raises(ValidationError):
        AlarmAnalysisResult.model_validate(raw_data)


@pytest.mark.parametrize("param", ["test", 123, None, False, " "])
def test_alarm_analysis_result_raises_on_invalid_priority(valid_analysis_result, param):
    raw_data = valid_analysis_result.model_dump()
    raw_data["priority"] = param
    with pytest.raises(ValidationError):
        AlarmAnalysisResult.model_validate(raw_data)


@pytest.mark.parametrize("param", ["a", 1, None, " "])
def test_alarm_analysis_result_raises_on_invalid_requires_review(
    valid_analysis_result, param
):
    raw_data = valid_analysis_result.model_dump()
    raw_data["requires_review"] = param
    with pytest.raises(ValidationError):
        AlarmAnalysisResult.model_validate(raw_data)


def test_alarm_analysis_result_raises_on_extra_field(valid_evaluation_case):
    raw_data = valid_evaluation_case.model_dump()
    raw_data["error_messages"] = "test"
    with pytest.raises(ValidationError):
        AlarmAnalysisResult.model_validate(raw_data)


def test_alarm_analysis_note_success(valid_analysis_result):
    raw_data = valid_analysis_result.model_dump()
    assert valid_analysis_result == AlarmAnalysisResult.model_validate(raw_data)


################### Evaluation Case Result ########################################################
@pytest.mark.parametrize("param", [" ", 1, None, True, ["test"]])
def test_evaluation_case_result_raises_on_invalid_id(valid_evaluation_case, param):
    raw_data = valid_evaluation_case.model_dump()
    raw_data["id"] = param
    with pytest.raises(ValidationError):
        EvaluationCaseResult.model_validate(raw_data)


@pytest.mark.parametrize("param", [None, "invalid", 123])
def test_evaluation_case_result_raises_on_invalid_expected(
    valid_evaluation_case, param
):
    raw_data = valid_evaluation_case.model_dump()
    raw_data["expected"] = param
    with pytest.raises(ValidationError):
        EvaluationCaseResult.model_validate(raw_data)


@pytest.mark.parametrize("param", [True, "invalid", 123])
def test_evaluation_case_result_raises_on_invalid_actual(valid_evaluation_case, param):
    raw_data = valid_evaluation_case.model_dump()
    raw_data["actual"] = param
    with pytest.raises(ValidationError):
        EvaluationCaseResult.model_validate(raw_data)


@pytest.mark.parametrize("param", [True, "invalid", 123])
def test_evaluation_case_result_raises_on_invalid_error_type(
    valid_evaluation_case, param
):
    raw_data = valid_evaluation_case.model_dump()
    raw_data["error_type"] = param
    with pytest.raises(ValidationError):
        EvaluationCaseResult.model_validate(raw_data)


@pytest.mark.parametrize("param", [True, 123])
def test_evaluation_case_result_raises_on_invalid_error_message(
    valid_evaluation_case, param
):
    raw_data = valid_evaluation_case.model_dump()
    raw_data["error_message"] = param
    with pytest.raises(ValidationError):
        EvaluationCaseResult.model_validate(raw_data)


def test_evaluation_case_result_raises_on_extra_field(valid_evaluation_case):
    raw_data = valid_evaluation_case.model_dump()
    raw_data["error_messages"] = "test"
    with pytest.raises(ValidationError):
        EvaluationCaseResult.model_validate(raw_data)


def test_evaluation_case_result_raises_when_actual_and_error_type_are_none(
    valid_evaluation_case,
):
    raw_data = valid_evaluation_case.model_dump()
    raw_data["actual"] = None
    raw_data["error_type"] = None
    with pytest.raises(ValidationError):
        EvaluationCaseResult.model_validate(raw_data)


def test_evaluation_case_resultactual_none_with_error_accepted(valid_evaluation_case):
    raw_data = valid_evaluation_case.model_dump()
    raw_data["actual"] = None
    raw_data["error_type"] = "timeout"
    result = EvaluationCaseResult.model_validate(raw_data)
    assert result.actual is None
    assert result.error_type == "timeout"


def test_evaluation_case_result_succes(valid_evaluation_case):
    raw_data = valid_evaluation_case.model_dump()
    EvaluationCaseResult.model_validate(raw_data)


################### Evaluation Stats ########################################################


@pytest.mark.parametrize("param", [" ", 123, True, None, 0.5])
def test_evaluation_stats_raises_on_invalid_llm_model(valid_evaluation_stats, param):
    raw_data = valid_evaluation_stats.model_dump()
    raw_data["llm_model"] = param
    with pytest.raises(ValidationError):
        EvaluationStats.model_validate(raw_data)


@pytest.mark.parametrize(
    "field",
    [
        "category_accuracy",
        "priority_accuracy",
        "requires_review_accuracy",
    ],
)
@pytest.mark.parametrize("param", [" ", 1.1, -1, True, None, "test"])
def test_evaluation_stats_raises_on_invalid_accuracy(
    valid_evaluation_stats, field, param
):
    raw_data = valid_evaluation_stats.model_dump()
    raw_data[field] = param
    with pytest.raises(ValidationError):
        EvaluationStats.model_validate(raw_data)


@pytest.mark.parametrize(
    "field",
    ["exact_match", "total_attempts", "failed_model", "failed_evidence", "results"],
)
@pytest.mark.parametrize("param", ["", "123", 0.5, True, None])
def test_evaluation_stats_raises_on_invalid_fields_values(
    valid_evaluation_stats, field, param
):
    raw_data = valid_evaluation_stats.model_dump()
    raw_data[field] = param
    with pytest.raises(ValidationError):
        EvaluationStats.model_validate(raw_data)


def test_evaluation_stats_raises_on_total_attempts_bigger_than_results(
    valid_evaluation_stats,
):
    raw_data = valid_evaluation_stats.model_dump()
    raw_data["total_attempts"] = len(raw_data["results"]) + 1
    with pytest.raises(ValidationError):
        EvaluationStats.model_validate(raw_data)


def test_evaluation_stats_raises_on_exact_match_bigger_than_total_attempts(
    valid_evaluation_stats,
):
    raw_data = valid_evaluation_stats.model_dump()
    raw_data["exact_match"] = raw_data["total_attempts"] + 1
    with pytest.raises(ValidationError):
        EvaluationStats.model_validate(raw_data)


def test_evaluation_stats_succes(valid_evaluation_stats):
    raw_data = valid_evaluation_stats.model_dump()
    EvaluationStats.model_validate(raw_data)
