import pytest, time


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
