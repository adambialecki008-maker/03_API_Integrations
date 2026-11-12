from webhooks.security import calculate_signature
import secrets

raw_body = b"The quick brown fox jumps over the lazy dog"
secret = "test_key"

print(calculate_signature(raw_body, secret))
secret = secrets.token_hex(32)
print(secret)
