from webhooks.security import (
    verify_webhook_signature,
    calculate_signature,
    is_timestamp_valid,
)
import hmac, hashlib, pytest


def test_verify_webhook_signature_accepts_valid_signature():
    raw_body = b"The quick brown fox jumps over the lazy dog"
    secret = "test_key"
    signature = calculate_signature(raw_body, secret)
    assert verify_webhook_signature(raw_body, signature, secret) is True


def test_calculate_signature():
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


@pytest.mark.parametrize(
    "timestamp, expected",
    [
        (1000, True),
        (800, True),
        (700, True),
        (699, False),
        (1300, True),
        (1301, False),
    ],
)
def test_is_timestamp_valid(timestamp, expected):
    assert is_timestamp_valid(timestamp, 1000) == expected
