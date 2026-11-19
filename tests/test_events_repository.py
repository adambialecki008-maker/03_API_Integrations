from api_integrations.events_repository import (
    EventsRepository,
    format_timestamp,
    DuplicateEventError,
)
import pytest
from api_integrations.models import (
    WebhookPayload,
    RegisteredEvent,
)
from unittest.mock import patch
from datetime import datetime


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
        "timestamp": 1794932369,
        "data": {
            "machine": "PLC_03",
            "alarm_code": 208,
        },
    }
    event_1 = WebhookPayload.model_validate(payload_1)
    event_2 = WebhookPayload.model_validate(payload_2)

    return event_1, event_2


@pytest.fixture
def valid_extra_events():
    payload_3 = {
        "event_id": "evt_003",
        "event": "alarm.created",
        "timestamp": 1794932360,
        "data": {
            "machine": "PLC_03",
            "alarm_code": 205,
        },
    }
    payload_4 = {
        "event_id": "evt_004",
        "event": "alarm.created",
        "timestamp": 1794932375,
        "data": {
            "machine": "PLC_04",
            "alarm_code": 208,
        },
    }
    event_3 = WebhookPayload.model_validate(payload_3)
    event_4 = WebhookPayload.model_validate(payload_4)

    return event_3, event_4


@pytest.fixture
def expected_events(valid_events):
    event_1, event_2 = valid_events
    expected_1 = RegisteredEvent(
        event_id=event_1.event_id,
        event=event_1.event,
        timestamp=format_timestamp(event_1.timestamp),
        data=event_1.data,
        received_at=format_timestamp(1794932368),
    )
    expected_2 = RegisteredEvent(
        event_id=event_2.event_id,
        event=event_2.event,
        timestamp=format_timestamp(event_2.timestamp),
        data=event_2.data,
        received_at=format_timestamp(1794932369),
    )
    return expected_1, expected_2


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


def test_save_event_adds_expected_event(repository, valid_events, expected_events):
    event_1, _ = valid_events
    expected_event, _ = expected_events
    with patch("time.time") as mock_time:
        mock_time.return_value = 1794932368
        repository.save_event(event_1)
        results, total = repository.get_events(event_id=event_1.event_id)
        assert results[0] == expected_event


def test_get_events_returns_none_if_no_event(repository):
    results, total = repository.get_events(event_id="evt_05")
    assert results == []


def test_save_event_raises_duplication_error_if_event_already_exists(
    repository, valid_events
):
    event_1, event_2 = valid_events
    repository.save_event(event_1)
    with pytest.raises(DuplicateEventError):
        repository.save_event(event_1)


def test_get_events_raises_if_date_from_is_higher_than_date_to(repository):
    time_from = datetime.fromisoformat("2026-11-18T08:31:00Z")
    time_to = datetime.fromisoformat("2026-11-18T08:30:00Z")
    with pytest.raises(ValueError, match="time_from cannot be later than time_to"):
        repository.get_events(time_from=time_from, time_to=time_to)


def test_get_events_gets_event_by_id(repository, valid_events, expected_events):
    event_1, event_2 = valid_events
    expected_1, _ = expected_events

    with patch("time.time") as mock_time:
        mock_time.return_value = event_1.timestamp
        repository.save_event(event_1)
        repository.save_event(event_2)
        results, total = repository.get_events(event_id=event_1.event_id)
        assert expected_1 == results[0]
        assert len(results) == 1


def test_get_events_by_machine_returns_expected_event(
    repository, valid_events, expected_events
):
    event_1, event_2 = valid_events
    _, expected_2 = expected_events
    with patch("time.time") as mock_time:
        mock_time.return_value = event_2.timestamp
        repository.save_event(event_1)
        repository.save_event(event_2)
        results, total = repository.get_events(machine=event_2.data.machine)
        expected_2.received_at = expected_2.timestamp
        assert expected_2 == results[0]
        assert len(results) == 1


def test_get_events_gets_events_by_time_from(repository, valid_events, expected_events):
    event_1, event_2 = valid_events
    expected_1, expected_2 = expected_events
    with patch("time.time") as mock_time:
        mock_time.return_value = 1794932370
        event_1.timestamp = 1794932370
        expected_1.timestamp = "2026-11-17T16:19:30+00:00"
        expected_1.received_at = expected_1.timestamp
        repository.save_event(event_1)
        repository.save_event(event_2)
        results, total = repository.get_events(time_from="2026-11-17T16:19:30+00:00")
        assert len(results) == 1
        assert results[0] == expected_1


def test_get_events_gets_events_by_time_to(repository, valid_events, expected_events):
    event_1, event_2 = valid_events
    expected_1, expected_2 = expected_events
    with patch("time.time") as mock_time:
        mock_time.return_value = 1794932369
        event_1.timestamp = 1794932370
        event_2.timestamp = 1794932369
        repository.save_event(event_1)
        repository.save_event(event_2)
        results, total = repository.get_events(time_to="2026-11-17T16:19:30+00:00")
        assert len(results) == 1
        assert results[0] == expected_2


def test_get_events_returns_without_exac_time_to(
    repository, valid_events, expected_events
):
    event_1, event_2 = valid_events
    expected_1, expected_2 = expected_events
    with patch("time.time") as mock_time:
        mock_time.return_value = 1794932368

        repository.save_event(event_1)
        repository.save_event(event_2)
        results, total = repository.get_events(time_to=expected_2.timestamp)
        assert len(results) == 1
        assert results[0] == expected_1


def test_get_events_gets_events_by_time_from_and_to(
    repository, valid_events, valid_extra_events, expected_events
):
    event_1, event_2 = valid_events
    event_3, event_4 = valid_extra_events
    expected_1, expected_2 = expected_events
    with patch("time.time") as mock_time:
        mock_time.return_value = event_1.timestamp
        repository.save_event(event_1)
        mock_time.return_value = event_2.timestamp
        repository.save_event(event_2)
        repository.save_event(event_3)
        repository.save_event(event_4)
        all_events, total = repository.get_events()
        assert len(all_events) == 4
        results, total = repository.get_events(
            time_from="2026-11-17T16:19:28+00:00", time_to="2026-11-17T16:19:30+00:00"
        )
        assert len(results) == 2
        assert results[0] == expected_2
        assert results[1] == expected_1


def test_get_events_gets_with_limit(
    repository, valid_events, valid_extra_events, expected_events
):
    event_1, event_2 = valid_events
    event_3, event_4 = valid_extra_events
    _, expected_2 = expected_events

    expected_4 = RegisteredEvent(
        event_id=event_4.event_id,
        event=event_4.event,
        timestamp=format_timestamp(event_4.timestamp),
        data=event_4.data,
        received_at=format_timestamp(1794932369),
    )
    with patch("time.time") as mock_time:
        mock_time.return_value = event_1.timestamp
        repository.save_event(event_1)
        mock_time.return_value = event_2.timestamp
        repository.save_event(event_2)
        repository.save_event(event_3)
        repository.save_event(event_4)
        all_events, total = repository.get_events()
        assert len(all_events) == 4
        results, total = repository.get_events(limit=2)
        assert len(results) == 2
        assert results[0] == expected_4
        assert results[1] == expected_2


def test_get_events_gets_with_limit_and_offset(
    repository, valid_events, valid_extra_events, expected_events
):
    event_1, event_2 = valid_events
    event_3, event_4 = valid_extra_events
    expected_1, expected_2 = expected_events
    expected_3 = RegisteredEvent(
        event_id=event_3.event_id,
        event=event_3.event,
        timestamp=format_timestamp(event_3.timestamp),
        data=event_3.data,
        received_at=format_timestamp(1794932369),
    )
    expected_4 = RegisteredEvent(
        event_id=event_4.event_id,
        event=event_4.event,
        timestamp=format_timestamp(event_4.timestamp),
        data=event_4.data,
        received_at=format_timestamp(1794932369),
    )
    with patch("time.time") as mock_time:
        mock_time.return_value = event_1.timestamp
        repository.save_event(event_1)
        mock_time.return_value = event_2.timestamp
        repository.save_event(event_2)
        repository.save_event(event_3)
        repository.save_event(event_4)
        all_events, total = repository.get_events()
        assert len(all_events) == 4
        results, total = repository.get_events(limit=10, offset=1)
        assert len(results) == 3
        assert results[0] == expected_2
        assert results[1] == expected_1
        assert results[2] == expected_3


def test_get_events_gets_correct_total(
    repository, valid_events, valid_extra_events, expected_events
):
    event_1, event_2 = valid_events
    event_3, event_4 = valid_extra_events
    expected_1, expected_2 = expected_events
    expected_3 = RegisteredEvent(
        event_id=event_3.event_id,
        event=event_3.event,
        timestamp=format_timestamp(event_3.timestamp),
        data=event_3.data,
        received_at=format_timestamp(1794932369),
    )
    expected_4 = RegisteredEvent(
        event_id=event_4.event_id,
        event=event_4.event,
        timestamp=format_timestamp(event_4.timestamp),
        data=event_4.data,
        received_at=format_timestamp(1794932369),
    )
    with patch("time.time") as mock_time:
        mock_time.return_value = event_1.timestamp
        repository.save_event(event_1)
        mock_time.return_value = event_2.timestamp
        repository.save_event(event_2)
        repository.save_event(event_3)
        repository.save_event(event_4)
        all_events, total = repository.get_events()
        assert len(all_events) == 4
        results, total = repository.get_events(limit=10, offset=1)
        assert len(results) == 3
        assert results[0] == expected_2
        assert results[1] == expected_1
        assert results[2] == expected_3
        assert total == 4
