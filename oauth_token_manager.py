import httpx
import time


class OAuth_token_manager:
    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.cached_token = None
        self.expires_at = 0

    def request_token_data(self) -> dict:
        url = "https://auth.example.com/oauth/token"
        data = {"grant_type": "client_credentials"}
        auth = (self.client_id, self.client_secret)
        response = httpx.post(url=url, timeout=10.0, data=data, auth=auth)
        response.raise_for_status()
        results = response.json()
        return results

    def get_token(self) -> str:
        if self.cached_token is not None and time.monotonic() < self.expires_at:
            return self.cached_token

        token_data = self.request_token_data()
        self.cached_token = token_data["access_token"]
        self.expires_in = token_data["expires_in"]
        self.expires_at = time.monotonic() + self.expires_in - 30
        return self.cached_token
