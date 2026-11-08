from webhook_handler import process_webhook
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


def test_process_webhook_succedes(valid_payload):
    expected_data = {
        "event_id": "evt_001",
        "machine": "PLC_01",
        "alarm_code": 204,
    }
    payload = valid_payload

    data = process_webhook(payload)
    assert data == expected_data


def test_process_webhook_raises_on_wrong_event(valid_payload):
    payload = valid_payload
    payload["event"] = "test"
    with pytest.raises(ValueError, match="Unsupported event"):
        process_webhook(valid_payload)


@pytest.fixture(params=["", "   ", 123, None, True])
def invalid_event_payload(request):
    return {
        "event_id": request.param,
        "event": "alarm.created",
        "data": {
            "machine": "PLC_01",
            "alarm_code": 204,
        },
    }


def test_process_webhook_raises_on_invalid_event_id(invalid_event_payload):
    with pytest.raises(ValueError):
        process_webhook(invalid_event_payload)


@pytest.fixture(params=("invalid_data", [None, [], "invalid", 123]))
def invalid_data_payload(request):
    return {"event_id": "evt_001", "event": "alarm.created", "data": request.param}


def test_process_webhook_raises_on_invalid_data(valid_payload, invalid_data_payload):
    valid_payload["data"] = invalid_data_payload
    with pytest.raises(ValueError):
        process_webhook(valid_payload)


@pytest.fixture(params=["", "   ", 123, None, True])
def invalid_data_payload_machine(request):
    return {
        "event_id": "evt_001",
        "event": "alarm.created",
        "data": {
            "machine": request.param,
            "alarm_code": 204,
        },
    }


def test_process_webhook_raises_on_invalid_data_machine(
    valid_payload, invalid_data_payload
):
    valid_payload["data"] = invalid_data_payload
    with pytest.raises(ValueError):
        process_webhook(valid_payload)


@pytest.fixture(params=["", "   ", "123", None, True])
def invalid_data_payload_alarm_code(request):
    return {
        "event_id": "evt_001",
        "event": "alarm.created",
        "data": {
            "machine": request.param,
            "alarm_code": 204,
        },
    }


def test_process_webhook_raises_on_invalid_data_alarm_code(
    valid_payload, invalid_data_payload
):
    valid_payload["data"] = invalid_data_payload
    with pytest.raises(ValueError):
        process_webhook(valid_payload)
