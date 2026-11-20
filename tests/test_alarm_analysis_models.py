from api_integrations.alarms_analysis.models import AlarmNoteAnalysis, AlarmNoteRequest
import pytest
from pydantic import ValidationError


@pytest.mark.parametrize("param", ["test", 123, None, False, " "])
def test_alarm_note_analysis_raises_on_incorrect_category(valid_alarm_note, param):
    raw_note = valid_alarm_note.model_dump()
    raw_note["category"] = param
    with pytest.raises(ValidationError):
        AlarmNoteAnalysis.model_validate(raw_note)


@pytest.mark.parametrize("param", ["test", 123, None, False, " "])
def test_alarm_note_analysis_raises_on_incorrect_priority(valid_alarm_note, param):
    raw_note = valid_alarm_note.model_dump()
    raw_note["priority"] = param
    with pytest.raises(ValidationError):
        AlarmNoteAnalysis.model_validate(raw_note)


@pytest.mark.parametrize("param", ["a" * 201, 123, None, False, " "])
def test_alarm_note_analysis_raises_on_incorrect_summary(valid_alarm_note, param):
    raw_note = valid_alarm_note.model_dump()
    raw_note["summary"] = param
    with pytest.raises(ValidationError):
        AlarmNoteAnalysis.model_validate(raw_note)


@pytest.mark.parametrize("param", ["a", 123, None, False, " ", [123], ["1"] * 4])
def test_alarm_note_analysis_raises_on_incorrect_evidence(valid_alarm_note, param):
    raw_note = valid_alarm_note.model_dump()
    raw_note["evidence"] = param
    with pytest.raises(ValidationError):
        AlarmNoteAnalysis.model_validate(raw_note)


@pytest.mark.parametrize("param", ["a", 1, None, " "])
def test_alarm_note_analysis_raises_on_incorrect_requires_review(
    valid_alarm_note, param
):
    raw_note = valid_alarm_note.model_dump()
    raw_note["requires_review"] = param
    with pytest.raises(ValidationError):
        AlarmNoteAnalysis.model_validate(raw_note)


@pytest.mark.parametrize(
    "summary,evidence",
    [("a" * 200, ["a"] * 3)],
)
def test_alarm_analysis_succees_with_boundary_conditions(
    valid_alarm_note, summary, evidence
):
    raw_note = valid_alarm_note.model_dump()
    raw_note["summary"] = summary
    raw_note["evidence"] = evidence
    AlarmNoteAnalysis.model_validate(raw_note)


@pytest.mark.parametrize("param", [0, ""])
def test_alarm_note_request_raises_invalid_data(param):
    with pytest.raises(ValidationError):
        AlarmNoteRequest.model_validate(param)
