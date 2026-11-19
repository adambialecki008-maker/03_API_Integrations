from api_integrations.security import calculate_signature
import secrets

from fastapi import FastAPI

app = FastAPI()
import api_integrations.webhooks.api
import api_integrations.events_history.api

if __name__ == "__main__":
    raw_body = b"The quick brown fox jumps over the lazy dog"
    secret = "test-key-123"

    print(calculate_signature(raw_body, secret))
    secret = secrets.token_hex(32)
    print(secret)
