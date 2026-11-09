from webhooks.models import WebhookPayload


def process_webhook(payload: WebhookPayload) -> dict:
    webhook = WebhookPayload.model_validate(payload)
    return {
        "event_id": webhook.event_id,
        "machine": webhook.data.machine,
        "alarm_code": webhook.data.alarm_code,
    }


def validate_payload(payload):
    if payload["event"] != "alarm.created":
        raise ValueError("Unsupported event")
    validate_event_id(payload["event_id"])
    validate_data(payload["data"])

    validate_data_machine(payload["data"]["machine"])
    validate_data_alarm_code(payload["data"]["alarm_code"])


def validate_event_id(event_id):
    if not isinstance(event_id, str):
        raise ValueError("Wrong ID format")
    if not event_id.strip():
        raise ValueError("Empty ID")


def validate_data(data):
    if not isinstance(data, dict):
        raise ValueError("Invalid data")
    if "machine" not in data or "alarm_code" not in data:
        raise ValueError("Invalid data")


def validate_data_machine(machine):
    if not isinstance(machine, str):
        raise ValueError("Invalid machine")
    if not machine.strip():
        raise ValueError("Invalid machine")


def validate_data_alarm_code(alarm_code):
    if not isinstance(alarm_code, int) or isinstance(alarm_code, bool):
        raise ValueError("Invalid alarm code")
