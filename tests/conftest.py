import pytest, time
from api_integrations.models import EventsHistoryRequest


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
