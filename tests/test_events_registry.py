from api_integrations.events_registry import EventRegistry
import time, pytest
from api_integrations.models import (
    RegisteredEvent,
    AlarmData,
    WebhookPayload,
)
from unittest.mock import patch
from api_integrations.events_repository import EventsRepository


@pytest.fixture
def valid_events():
    payload_1 = {
        "event_id": "evt_001",
        "event": "alarm.created",
        "timestamp": int(time.time()),
        "data": {
            "machine": "PLC_01",
            "alarm_code": 204,
        },
    }
    payload_2 = {
        "event_id": "evt_002",
        "event": "alarm.created",
        "timestamp": int(time.time()),
        "data": {
            "machine": "PLC_03",
            "alarm_code": 208,
        },
    }
    event_1 = WebhookPayload.model_validate(payload_1)
    event_2 = WebhookPayload.model_validate(payload_2)

    return event_1, event_2


@pytest.fixture
def expected_event():

    return RegisteredEvent(
        event_id="evt_001",
        event="alarm.created",
        timestamp="17-11-2026 13:42:09",
        data=AlarmData(machine="PLC_01", alarm_code=204),
        received_at="17-11-2026 13:42:09",
    )


def test_event_registry_returns_none(valid_events, tmp_path, monkeypatch):
    test_path = tmp_path / "test.db"
    registry = EventRegistry()
    test_path = tmp_path / "test.db"
    monkeypatch.setattr(
        "api_integrations.events_registry.EventsRepository",
        lambda: EventsRepository(path=test_path),
    )

    event_1, event_2 = valid_events
    assert registry.register(event_1) is True
    assert registry.register(event_1) is False
    assert registry.register(event_2) is True
