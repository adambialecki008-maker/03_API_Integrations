from webhooks.models import AlarmData, WebhookPayload
import pytest
from pydantic import ValidationError


def test_webhook_model_valid_data(valid_payload):
    webhook = WebhookPayload.model_validate(valid_payload)
    assert webhook.model_dump() == valid_payload

    valid_payload["data"]["machine"] = "  PLC_01  "
    webhook = WebhookPayload.model_validate(valid_payload)

    assert webhook.data.machine == "PLC_01"


@pytest.mark.parametrize("invalid_id", [" ", 123, None])
def test_webhook_models_rejects_invalid_id(valid_payload, invalid_id):
    payload = valid_payload
    payload["event_id"] = invalid_id
    with pytest.raises(ValidationError):
        webhook = WebhookPayload.model_validate(payload)


@pytest.mark.parametrize("invalid_code", ["204", 204.5, None, True])
def test_webhook_rejects_invalid_alarm_code(valid_payload, invalid_code):
    payload = valid_payload
    payload["data"]["alarm_code"] = invalid_code
    with pytest.raises(ValidationError):
        webhook = WebhookPayload.model_validate(payload)


@pytest.mark.parametrize("invalid_machine", ["", "   ", None])
def test_webhook_rejects_invalid_machine(valid_payload, invalid_machine):
    payload = valid_payload
    payload["data"]["machine"] = invalid_machine
    with pytest.raises(ValidationError):
        webhook = WebhookPayload.model_validate(payload)
