from fastapi import Header, Request, HTTPException
from api_integrations.webhooks.handler import process_webhook
from api_integrations.webhooks.models import WebhookPayload
from api_integrations.security import (
    verify_signature,
    is_timestamp_valid,
)
import os, time
from dotenv import load_dotenv
from pydantic import ValidationError
from api_integrations.events_registry import EventRegistry
from api_integrations.main import app

load_dotenv()
secret = os.environ["WEBHOOK_SECRET"]

registry = EventRegistry()


@app.post("/webhook")
async def receive_webhook(
    request: Request,
    signature: str | None = Header(
        default=None,
        alias="X-Webhook-Signature",
    ),
):
    raw_body = await request.body()
    if not signature or not verify_signature(raw_body, signature, secret):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")
    try:
        payload = WebhookPayload.model_validate_json(raw_body)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail="Invalid webhook payload") from e
    current_time = int(time.time())
    if not is_timestamp_valid(payload.timestamp, current_time):
        raise HTTPException(status_code=401, detail="Expired webhook timestamp")
    if not registry.register(payload):
        raise HTTPException(
            status_code=409,
            detail="Duplicate webhook event",
        )

    return process_webhook(payload)
