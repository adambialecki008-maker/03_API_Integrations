from fastapi.testclient import TestClient
from api_integrations.main import app
from api_integrations.alarms_analysis.api import post_analyzed_note, secret
import pytest, json
from api_integrations.alarms_analysis.models import AlarmNoteRequest, AlarmNoteAnalysis
from pydantic import ValidationError
from unittest.mock import patch

client = TestClient(app)


def test_post_analyzed_note_raises_http_401_if_no_key():
    note = "PLC_01 - Conveyor stopped after motor overload protection tripped. Operator requests an electrical inspection before restarting the line."
    content = AlarmNoteRequest(note=note).model_dump_json()
    headers = {"Content-Type": "application/json"}
    response = client.post("/analyze_note", content=content, headers=headers)
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid analzye_api_key"}


def test_post_analyzed_note_raises_http_401_if_invalid_key():
    note = "PLC_01 - Conveyor stopped after motor overload protection tripped. Operator requests an electrical inspection before restarting the line."
    content = AlarmNoteRequest(note=note).model_dump_json()
    headers = {"Content-Type": "application/json", "X-API-Key": "Invalid"}
    response = client.post("/analyze_note", content=content, headers=headers)
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid analzye_api_key"}


def test_post_analyzed_note_raises_http_422_if_no_content():
    headers = {"Content-Type": "application/json", "X-API-Key": secret}
    response = client.post("/analyze_note", headers=headers)
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {"type": "missing", "loc": ["body"], "msg": "Field required", "input": None}
        ]
    }


def test_post_analyzed_note_raises_http_422_if_invalid_json():
    headers = {"Content-Type": "application/json", "X-API-Key": secret}
    response = client.post(
        "/analyze_note", headers=headers, json={"invalid": "invalid"}
    )
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "type": "missing",
                "loc": ["body", "note"],
                "msg": "Field required",
                "input": None,
                "input": {"invalid": "invalid"},
            }
        ]
    }


def test_post_analyzed_note_raises_http_422_if_validation_error():
    note = "PLC_01 - Conveyor stopped after motor overload protection tripped. Operator requests an electrical inspection before restarting the line."
    headers = {"Content-Type": "application/json", "X-API-Key": secret}
    content = AlarmNoteRequest(note=note).model_dump_json()
    try:
        AlarmNoteAnalysis.model_validate(
            {
                "category": "invalid_category",
                "priority": "unknown",
                "summary": "Test",
                "evidence": [],
                "requires_review": True,
            }
        )
    except ValidationError as exc:
        validation_error = exc
    with patch(
        "api_integrations.alarms_analysis.api.analyze_alarm_note"
    ) as mock_analyzer:
        mock_analyzer.side_effect = validation_error
        response = client.post("/analyze_note", headers=headers, content=content)
    assert response.status_code == 422


def test_post_analyzed_note_raises_http_422_if_value_error():
    note = "PLC_01 - Conveyor stopped after motor overload protection tripped. Operator requests an electrical inspection before restarting the line."
    headers = {"Content-Type": "application/json", "X-API-Key": secret}
    content = AlarmNoteRequest(note=note).model_dump_json()
    try:
        evidence = "not in note"
        if evidence not in note:
            raise ValueError("Invalid evidence")
    except ValueError as exc:
        value_error = exc
    with patch(
        "api_integrations.alarms_analysis.api.analyze_alarm_note"
    ) as mock_analyzer:
        mock_analyzer.side_effect = value_error
        response = client.post("/analyze_note", headers=headers, content=content)
    assert response.status_code == 502


def test_post_analyzed_note_succes(valid_alarm_note):
    note = "PLC_01 - Conveyor stopped after motor overload protection tripped. Operator requests an electrical inspection before restarting the line."
    headers = {"Content-Type": "application/json", "X-API-Key": secret}
    expected = valid_alarm_note.model_dump()
    content = AlarmNoteRequest(note=note).model_dump_json()
    with patch(
        "api_integrations.alarms_analysis.api.analyze_alarm_note"
    ) as mock_analyzer:
        mock_analyzer.return_value = valid_alarm_note
        response = client.post("/analyze_note", headers=headers, content=content)
    assert response.status_code == 200
    assert response.json() == expected
