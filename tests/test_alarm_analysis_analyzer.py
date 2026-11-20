import pytest
from api_integrations.alarms_analysis.analyzer import analyze_alarm_note
from api_integrations.alarms_analysis.models import AlarmNoteAnalysis
from unittest.mock import patch


def test_alarm_analyzer_returns_expected_data(valid_alarm_note):
    note = "PLC_02 - Unusual vibration and grinding noise detected near the conveyor gearbox. Maintenance suspects a worn bearing. Machine stopped for inspection."
    valid_alarm_note.evidence = [
        "PLC_02",
        "Unusual vibration",
        "grinding noise detected",
    ]
    test_json = valid_alarm_note.model_dump_json()
    with patch("ollama.chat") as mock_chat:
        mock_chat.return_value = {
            "message": {
                "content": test_json,
            },
        }
        result = analyze_alarm_note(note)
    assert result == valid_alarm_note


def test_alarm_analyzer_raises_on_evidence_not_in_note(valid_alarm_note):
    note = "PLC_02 - Unusual vibration and grinding noise detected near the conveyor gearbox. Maintenance suspects a worn bearing. Machine stopped for inspection."
    test_json = valid_alarm_note.model_dump_json()
    with patch("ollama.chat") as mock_chat:
        mock_chat.return_value = mock_chat.return_value = {
            "message": {
                "content": test_json,
            },
        }
        with pytest.raises(ValueError):
            analyze_alarm_note(note)
