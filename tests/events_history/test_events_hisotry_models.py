import pytest
from api_integrations.events_history.models import (
    RegisteredEvent,
    TimestampUTC,
    EventsHistoryRequest,
)
from pydantic import ValidationError, TypeAdapter
from api_integrations.webhooks.models import WebhookPayload, AlarmData


#######RegisteredEvent###############################################################
#####################################################################################
@pytest.fixture
def valid_registered_event():

    return RegisteredEvent(
        event_id="evt_001",
        event="alarm.created",
        timestamp="2026-11-17T16:19:30+00:00",
        data=AlarmData(machine="PLC_01", alarm_code=204),
        received_at="2026-11-17T16:19:30+00:00",
    )


def test_registered_event_model_valid_data(valid_registered_event):
    event = RegisteredEvent.model_validate(valid_registered_event)
    assert event == valid_registered_event

    raw_event = valid_registered_event.model_dump()
    raw_event["data"]["machine"] = "  PLC_01  "
    event = RegisteredEvent.model_validate(raw_event)
    assert event.data.machine == "PLC_01"


@pytest.mark.parametrize("invalid_id", [" ", 123, None])
def test_registered_event_models_rejects_invalid_id(valid_registered_event, invalid_id):
    raw_event = valid_registered_event.model_dump()
    raw_event["event_id"] = invalid_id
    with pytest.raises(ValidationError):
        event = RegisteredEvent.model_validate(raw_event)


@pytest.mark.parametrize("invalid_code", ["204", 204.5, None, True])
def test_registered_event_rejects_invalid_alarm_code(
    valid_registered_event, invalid_code
):
    raw_event = valid_registered_event.model_dump()
    raw_event["data"]["alarm_code"] = invalid_code
    with pytest.raises(ValidationError):
        event = RegisteredEvent.model_validate(raw_event)


@pytest.mark.parametrize("invalid_machine", ["", "   ", None])
def test_registered_event_rejects_invalid_machine(
    valid_registered_event, invalid_machine
):
    raw_event = valid_registered_event.model_dump()
    raw_event["data"]["machine"] = invalid_machine
    with pytest.raises(ValidationError):
        event = RegisteredEvent.model_validate(raw_event)


@pytest.mark.parametrize("timestamp", ["1000", 1000.5, None, True])
def test_registered_event_rejects_invalid_timestamp_format(
    valid_registered_event, timestamp
):
    raw_event = valid_registered_event.model_dump()
    raw_event["timestamp"] = timestamp
    with pytest.raises(ValidationError):
        event = RegisteredEvent.model_validate(raw_event)


@pytest.mark.parametrize("received_at", ["1000", 1000.5, None, True])
def test_registered_event_rejects_invalid_received_at_format(
    valid_registered_event, received_at
):
    raw_event = valid_registered_event.model_dump()
    raw_event["received_at"] = received_at
    with pytest.raises(ValidationError):
        event = RegisteredEvent.model_validate(raw_event)


timestamp_adapter = TypeAdapter(TimestampUTC)


@pytest.mark.parametrize(
    "invalid_input",
    [
        1000,
        "2026-11-18T15:30:00",
        "not-a-date",
        1000.5,
        1700000000,
        True,
    ],
)
def test_timestamp_utc_rejects_invalid_format(invalid_input):
    with pytest.raises(ValidationError):
        timestamp_adapter.validate_python(invalid_input)


@pytest.mark.parametrize(
    ("input_dt", "expected_utc"),
    [
        ("2026-11-18T16:30:00+01:00", "2026-11-18T15:30:00+00:00"),
        ("2026-11-18T10:30:00-05:00", "2026-11-18T15:30:00+00:00"),
        ("2026-11-18T15:30:00Z", "2026-11-18T15:30:00+00:00"),
    ],
)
def test_timestamp_utc_normalizes_to_utc(input_dt, expected_utc):
    assert timestamp_adapter.validate_python(input_dt) == expected_utc


def test_time_registered_rejects_none():
    with pytest.raises(ValidationError):
        timestamp_adapter.validate_python(None)


#######EventsHistoryRequest##########################################################
#####################################################################################


@pytest.fixture
def valid_history_request():
    return EventsHistoryRequest(
        event_id="evt_001",
        machine="PLC_01",
        time_from="2026-11-17T16:19:20+00:00",
        time_to="2026-11-17T16:19:30+00:00",
        limit=10,
    )
