import pytest


@pytest.fixture
def valid_payload():
    return {
        "event_id": "evt_001",
        "event": "alarm.created",
        "data": {
            "machine": "PLC_01",
            "alarm_code": 204,
        },
    }
