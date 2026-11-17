from webhooks.models import WebhookPayload


def process_webhook(payload: WebhookPayload) -> dict:
    webhook = WebhookPayload.model_validate(payload)
    return {
        "event_id": webhook.event_id,
        "machine": webhook.data.machine,
        "alarm_code": webhook.data.alarm_code,
    }
