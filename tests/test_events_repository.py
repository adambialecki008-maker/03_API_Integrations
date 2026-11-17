from api_integrations.events_repository import (
    EventsRepository,
    format_timestamp,
    DuplicateEventError,
)
import pytest, time
from api_integrations.models import WebhookPayload, RegisteredEvent, AlarmData
from unittest.mock import patch


@pytest.fixture
def repository(tmp_path):
    test_path = tmp_path / "test.db"
    repository = EventsRepository(test_path)
    return repository


@pytest.fixture
def valid_events():
    payload_1 = {
        "event_id": "evt_001",
        "event": "alarm.created",
        "timestamp": 1794932368,
        "data": {
            "machine": "PLC_01",
            "alarm_code": 204,
        },
    }
    payload_2 = {
        "event_id": "evt_002",
        "event": "alarm.created",
        "timestamp": 1794932368,
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
        timestamp=format_timestamp(1794932368),
        data=AlarmData(machine="PLC_01", alarm_code=204),
        received_at=format_timestamp(1794932368),
    )


def test_creates_table_crates_expected_columns(repository):
    expected_columns = [
        ("id", "INTEGER", 0, None, 1),
        ("event_id", "TEXT", 1, None, 0),
        ("event", "TEXT", 1, None, 0),
        ("machine", "TEXT", 1, None, 0),
        ("alarm_code", "INT", 1, None, 0),
        ("timestamp", "TEXT", 1, None, 0),
        ("received_at", "TEXT", 1, None, 0),
    ]
    connection = repository.connect()
    cursor = connection.cursor()
    cursor.execute("PRAGMA table_info(events)")
    existing_columns = [row[1:] for row in cursor.fetchall()]
    assert existing_columns == expected_columns


def test_save_event_adds_expected_event(repository, valid_events, expected_event):
    event_1, _ = valid_events
    with patch("time.time") as mock_time:
        mock_time.return_value = 1794932368
        repository.save_event(event_1)
        results = repository.get_event_by_event_id(event_1.event_id)
        assert results == expected_event


def test_get_event_by_id_returns_none_if_no_event(repository):
    results = repository.get_event_by_event_id("evt_05")
    assert results is None


def test_save_event_raises_duplication_error_if_event_already_exists(
    repository, valid_events
):
    event_1, event_2 = valid_events
    repository.save_event(event_1)
    with pytest.raises(DuplicateEventError):
        repository.save_event(event_1)
