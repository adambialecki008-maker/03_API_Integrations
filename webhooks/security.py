import hmac
import hashlib


def verify_webhook_signature(raw_body: bytes, signature: str, secret: str) -> bool:
    secret_byte = secret.encode("utf-8")
    body_hmac = hmac.new(secret_byte, raw_body, hashlib.sha256)
    body_hex = body_hmac.hexdigest()
    return hmac.compare_digest(body_hex, signature)


def calculate_signature(raw_body: bytes, secret: str) -> str:
    return hmac.new(secret.encode("utf-8"), raw_body, hashlib.sha256).hexdigest()
