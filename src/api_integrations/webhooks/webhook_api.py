from fastapi import FastAPI, Header, Request, HTTPException
from webhooks.webhook_handler import process_webhook
from webhooks.models import WebhookPayload
from webhooks.security import verify_webhook_signature, is_timestamp_valid
import os, time
from dotenv import load_dotenv
from pydantic import ValidationError
from webhooks.duplication import EventRegistry

app = FastAPI()
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
    if not signature or not verify_webhook_signature(raw_body, signature, secret):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")
    try:
        payload = WebhookPayload.model_validate_json(raw_body)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail="Invalid webhook payload") from e
    current_time = int(time.time())
    if not is_timestamp_valid(payload.timestamp, current_time):
        raise HTTPException(status_code=401, detail="Expired webhook timestamp")
    if not registry.register(payload.event_id):
        raise HTTPException(
            status_code=409,
            detail="Duplicate webhook event",
        )
    return process_webhook(payload)
