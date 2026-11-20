import pytest, time
from api_integrations.models import EventsHistoryRequest
from api_integrations.alarms_analysis.models import AlarmNoteAnalysis


@pytest.fixture
def valid_payload():
    return {
        "event_id": "evt_001",
        "event": "alarm.created",
        "timestamp": int(time.time()),
        "data": {
            "machine": "PLC_01",
            "alarm_code": 204,
        },
    }


@pytest.fixture
def valid_history_request():
    return EventsHistoryRequest(
        event_id="evt_001",
        machine="PLC_01",
        time_from="2026-11-17T16:19:20+00:00",
        time_to="2026-11-17T16:19:30+00:00",
        limit=10,
    )


@pytest.fixture
def valid_alarm_note():
    return AlarmNoteAnalysis(
        category="electrical",
        priority="high",
        summary="Test sumamry",
        evidence=["ev_1", "ev_2", "ev_3"],
        requires_review=False,
    )
