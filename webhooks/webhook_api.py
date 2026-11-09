from fastapi import FastAPI, HTTPException
from webhooks.webhook_handler import process_webhook
from webhooks.models import WebhookPayload

app = FastAPI()


@app.post("/webhook")
def receive_webhook(payload: WebhookPayload):
    return process_webhook(payload)
