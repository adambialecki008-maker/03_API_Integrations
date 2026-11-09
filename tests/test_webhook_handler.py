from webhooks.webhook_handler import process_webhook
from webhooks.models import WebhookPayload


def test_process_webhook_succedes(valid_payload):
    expected_data = {
        "event_id": "evt_001",
        "machine": "PLC_01",
        "alarm_code": 204,
    }
    payload = WebhookPayload.model_validate(valid_payload)

    data = process_webhook(payload)
    assert data == expected_data
