from oauth_token_manager import OAuth_token_manager
import pytest
from unittest.mock import patch, call
import httpx


@pytest.fixture
def manager():
    client_id = "id_test123"
    client_secret = "secret_test123"
    return OAuth_token_manager(client_id, client_secret)


@pytest.fixture
def post_error_401():
    request = httpx.Request(method="POST", url="test")
    response = httpx.Response(status_code=401, request=request)
    return httpx.HTTPStatusError(
        message="Error 401", request=request, response=response
    )


def test_oauth_token_manager_init(manager):
    client_id = "id_test123"
    client_secret = "secret_test123"

    assert manager.client_id == client_id
    assert manager.client_secret == client_secret
    assert manager.cached_token is None
    assert manager.expires_at == 0


def test_request_token_data_returns_expected_data(manager):
    expected_data = {
        "access_token": "test_token",
        "token_type": "Bearer",
        "expires_in": 3600,
    }
    with patch("httpx.post") as mock_post:
        mock_post.return_value.json.return_value = expected_data
        data = manager.request_token_data()
        assert data == expected_data
        mock_post.assert_called_once_with(
            url="https://auth.example.com/oauth/token",
            timeout=10.0,
            data={"grant_type": "client_credentials"},
            auth=("id_test123", "secret_test123"),
        )
        mock_post.return_value.raise_for_status.assert_called_once()


def test_request_token_data_raises_on_http_401(manager, post_error_401):
    with patch("httpx.post") as mock_post:
        mock_post.return_value.raise_for_status.side_effect = post_error_401
        with pytest.raises(httpx.HTTPStatusError):
            manager.request_token_data()


def test_request_token_data_raises_on_timeout(manager):
    with patch("httpx.post") as mock_post:
        mock_post.side_effect = httpx.ReadTimeout("Timeout Reached")
        with pytest.raises(httpx.TimeoutException):
            manager.request_token_data()


def test_get_token_returns_expected_data_if_no_cached_token_exists(manager):
    example_data = {"access_token": "test_token", "expires_in": 3600}
    with patch.object(manager, "request_token_data") as mock_data:
        with patch("oauth_token_manager.time.monotonic") as mock_monotonic:
            mock_monotonic.return_value = 1000
            mock_data.return_value = example_data
            data = manager.get_token()
            assert data == example_data["access_token"]
            assert manager.cached_token == data
            mock_data.assert_called_once_with()
            assert manager.expires_at == 4570


def test_get_token_uses_cached_token(manager):
    old_data = {"access_token": "token_1", "expires_in": 3600}
    new_data = {"access_token": "token_2", "expires_in": 3600}
    with patch.object(manager, "request_token_data") as mock_data:
        with patch("oauth_token_manager.time.monotonic") as mock_monotonic:
            mock_monotonic.return_value = 1000
            mock_data.return_value = old_data
            data = manager.get_token()
            mock_data.return_value = new_data
            mock_monotonic.return_value = 2000
            data = manager.get_token()
            assert data == old_data["access_token"]
            mock_data.assert_called_once_with()
            assert manager.cached_token == data
            assert manager.expires_at == 4570


def test_get_token_refreshes_token_after_time(manager):
    old_data = {"access_token": "token_1", "expires_in": 3600}
    new_data = {"access_token": "token_2", "expires_in": 3600}
    with patch.object(manager, "request_token_data") as mock_data:
        with patch("oauth_token_manager.time.monotonic") as mock_monotonic:
            mock_monotonic.return_value = 1000
            mock_data.side_effect = [old_data, new_data]
            data = manager.get_token()
            assert data == old_data["access_token"]
            mock_data.assert_called_once_with()
            assert manager.cached_token == data
            assert manager.expires_at == 4570
            mock_monotonic.return_value = 5000
            data = manager.get_token()
            assert data == new_data["access_token"]
            assert mock_data.call_count == 2
            assert manager.cached_token == data
            assert manager.expires_at == 8570


def test_get_token_refreshes_at_expiration_boundary(manager):
    old_data = {"access_token": "token_1", "expires_in": 3600}
    new_data = {"access_token": "token_2", "expires_in": 3600}
    with patch.object(manager, "request_token_data") as mock_data:
        with patch("oauth_token_manager.time.monotonic") as mock_monotonic:
            mock_monotonic.return_value = 1000
            mock_data.side_effect = [old_data, new_data]
            data = manager.get_token()
            mock_data.assert_called_once_with()
            assert data == old_data["access_token"]
            assert manager.cached_token == data
            assert manager.expires_at == 4570
            mock_monotonic.return_value = 4570
            data = manager.get_token()
            assert data == new_data["access_token"]
            assert mock_data.call_count == 2
            assert manager.cached_token == data
            assert manager.expires_at == 8140
