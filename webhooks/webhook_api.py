from fastapi import FastAPI, Header, Request, HTTPException
from webhooks.webhook_handler import process_webhook
from webhooks.models import WebhookPayload
from webhooks.security import verify_webhook_signature
import os
from dotenv import load_dotenv
from pydantic import ValidationError

app = FastAPI()
load_dotenv()
secret = os.environ["WEBHOOK_SECRET"]


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
    return process_webhook(payload)
