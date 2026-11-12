from webhooks.security import verify_webhook_signature, calcualte_signature
import hmac
import hashlib


def test_verify_webhook_signature_accepts_valid_signature():
    raw_body = b"The quick brown fox jumps over the lazy dog"
    secret = "test_key"
    signature = calcualte_signature(raw_body, secret)
    assert verify_webhook_signature(raw_body, signature, secret) is True


def test_calcualte_signature():
    expected_signature = (
        "dec34d4a158519016d64c1546d65edb893e20720c297cd64a5504d4542268f27"
    )
    raw_body = b"The quick brown fox jumps over the lazy dog"
    secret = "test_key"
    signature = hmac.new(secret.encode("utf-8"), raw_body, hashlib.sha256).hexdigest()
    assert signature == expected_signature


def test_verify_webhook_signature_rejects_modified_body():
    body_old = b"Alarm_204"
    body_new = b"Alarm_205"
    secret = "key"
    signature = hmac.new(secret.encode("utf-8"), body_old, hashlib.sha256).hexdigest()
    assert verify_webhook_signature(body_new, signature, secret) is False
