from unittest.mock import patch, call
from api_client import (
    fetch_users,
    fetch_posts_by_user,
    fetch_headers,
    get_api_key,
    create_post,
    fetch_post_page,
    fetch_all_posts,
    fetch_post_page_with_retry,
)
import httpx
import pytest


def test_fetch_users_returns_expected_data():
    example_data = [
        {"id": 1, "name": "Adam", "email": "adam@example.com", "username": "test123"},
        {"id": 2, "name": "John", "email": "john@example.com", "username": "john123"},
    ]

    expected_data = [
        {"id": 1, "name": "Adam", "email": "adam@example.com"},
        {"id": 2, "name": "John", "email": "john@example.com"},
    ]
    with patch("httpx.get") as mock_get:
        mock_get.return_value.json.return_value = example_data
        data = fetch_users()
        mock_get.return_value.raise_for_status.assert_called_once()
    assert data == expected_data


def test_fetch_users_raises_on_http_404():
    request = httpx.Request("GET", "https://jsonplaceholder.typicode.com/users")
    response = httpx.Response(status_code=404, request=request)
    with patch("httpx.get") as mock_get:
        mock_get.return_value.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Error 404", request=request, response=response
        )
        with pytest.raises(httpx.HTTPStatusError):
            fetch_users()


def test_fetch_users_raises_on_timeout():
    with patch("httpx.get") as mock_get:
        mock_get.side_effect = httpx.ReadTimeout("Timed out")
        with pytest.raises(httpx.TimeoutException):
            fetch_users()


def test_fetch_posts_by_user_returns_expected_data():
    example_data = [
        {"userId": 2, "id": 11, "title": "Post A", "body": "Text A"},
        {"userId": 2, "id": 12, "title": "Post B", "body": "Text B"},
    ]
    expected_data = [
        {"id": 11, "title": "Post A"},
        {"id": 12, "title": "Post B"},
    ]
    with patch("httpx.get") as mock_get:
        mock_get.return_value.json.return_value = example_data
        data = fetch_posts_by_user(2)
        mock_get.return_value.raise_for_status.assert_called_once()
        mock_get.assert_called_once_with(
            url="https://jsonplaceholder.typicode.com/posts",
            timeout=10.0,
            params={"userId": 2},
        )
    assert data == expected_data


def test_fetch_posts_by_user_raises_on_http_404():
    request = httpx.Request("GET", "https://jsonplaceholder.typicode.com/posts")
    response = httpx.Response(status_code=404, request=request)
    with patch("httpx.get") as mock_get:
        mock_get.return_value.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Error 404", request=request, response=response
        )
        with pytest.raises(httpx.HTTPStatusError):
            fetch_posts_by_user(2)


def test_fetch_posts_by_user_raises_on_timeout():
    with patch("httpx.get") as mock_get:
        mock_get.side_effect = httpx.ReadTimeout("Timed out")
        with pytest.raises(httpx.TimeoutException):
            fetch_posts_by_user(2)


def test_fetch_headers_returns_expecte_data():
    example_data = {
        "headers": {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate",
            "Host": "httpbin.org",
            "User-Agent": "python-httpx/0.28.1",
            "X-Api-Key": "test-key-123",
        }
    }
    expected_data = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate",
        "Host": "httpbin.org",
        "User-Agent": "python-httpx/0.28.1",
        "X-Api-Key": "test-key-123",
    }
    with patch("httpx.get") as mock_get:
        mock_get.return_value.json.return_value = example_data
        data = fetch_headers("test-key-123")
        mock_get.return_value.raise_for_status.assert_called_once()
        mock_get.assert_called_once_with(
            url="https://httpbin.org/headers",
            timeout=10.0,
            headers={"X-API-KEY": "test-key-123"},
        )
    assert data == expected_data


def test_fetch_headers_raises_on_http_404():
    request = httpx.Request(method="GET", url="https://httpbin.org/headers")
    response = httpx.Response(status_code=404, request=request)
    with patch("httpx.get") as mock_get:
        mock_get.return_value.raise_for_status.side_effect = httpx.HTTPStatusError(
            message="Error 404", request=request, response=response
        )
        with pytest.raises(httpx.HTTPStatusError):
            fetch_headers("test-key-123")


def test_fetch_headers_raises_on_timeout():
    with patch("httpx.get") as mock_get:
        mock_get.side_effect = httpx.ReadTimeout("Timeout Reached")
        with pytest.raises(httpx.TimeoutException):
            fetch_headers("test-key-123")


def test_get_api_key_returns_valid_key(monkeypatch):
    test_key = "test_key_123"
    monkeypatch.setenv("API_KEY", test_key)
    assert test_key == get_api_key()


def test_get_api_key_raises_if_there_is_no_key(monkeypatch):
    monkeypatch.delenv("API_KEY", raising=False)
    with pytest.raises(ValueError):
        get_api_key()


def test_get_api_key_raises_if_key_is_empty(monkeypatch):
    monkeypatch.setenv("API_KEY", "  ")
    with pytest.raises(ValueError):
        get_api_key()


def test_create_post_returns_exected_response():
    example_data = {"userId": 1, "title": "Test", "body": "Hello world"}
    expected_data = {"userId": 1, "title": "Test", "body": "Hello world", "id": 101}
    with patch("httpx.post") as mock_post:
        mock_post.return_value.json.return_value = expected_data
        data = create_post(1, "Test", "Hello world")
        mock_post.return_value.raise_for_status.assert_called_once()
        mock_post.assert_called_once_with(
            url="https://jsonplaceholder.typicode.com/posts",
            json=example_data,
            timeout=10.0,
        )
    assert data == expected_data


def test_create_post_raises_on_http_404():
    request = httpx.Request(
        method="POST", url="https://jsonplaceholder.typicode.com/posts"
    )
    respone = httpx.Response(status_code=404, request=request)
    with patch("httpx.post") as mock_post:
        mock_post.return_value.raise_for_status.side_effect = httpx.HTTPStatusError(
            message="Error 404", response=respone, request=request
        )
        with pytest.raises(httpx.HTTPStatusError):
            create_post(1, "Test", "Hello world")


def test_create_post_raises_tiemout():
    with patch("httpx.post") as mock_post:
        mock_post.side_effect = httpx.ReadTimeout("Timeout reached")
        with pytest.raises(httpx.TimeoutException):
            create_post(1, "Test", "Hello world")


def test_fetch_post_page_returns_expected_data():
    example_data = [
        {"userId": 1, "id": 4, "title": "eum et est occaecati", "body": "Test body"},
        {"userId": 1, "id": 5, "title": "nesciunt quas odio", "body": "Test body"},
        {"userId": 1, "id": 6, "title": "dolorem eum magni", "body": "Test body"},
    ]
    expected_data = [
        {"id": 4, "title": "eum et est occaecati"},
        {"id": 5, "title": "nesciunt quas odio"},
        {"id": 6, "title": "dolorem eum magni"},
    ]
    with patch("httpx.get") as mock_get:
        mock_get.return_value.json.return_value = example_data
        data = fetch_post_page(2, 3)
        mock_get.return_value.raise_for_status.assert_called_once()
        url = "https://jsonplaceholder.typicode.com/posts"
        params = {"_page": 2, "_limit": 3}
        mock_get.assert_called_once_with(
            url=url,
            params=params,
            timeout=10.0,
        )
    assert data == expected_data


def test_fetch_post_page_raises_on_http_404():
    url = "https://jsonplaceholder.typicode.com/posts"
    request = httpx.Request(method="GET", url=url)
    response = httpx.Response(status_code=404, request=request)
    with patch("httpx.get") as mock_get:
        mock_get.return_value.raise_for_status.side_effect = httpx.HTTPStatusError(
            message="Error 404",
            request=request,
            response=response,
        )
        with pytest.raises(httpx.HTTPStatusError):
            fetch_post_page(2, 3)


def test_fetch_post_page_raises_on_timeout():
    with patch("httpx.get") as mock_get:
        mock_get.side_effect = httpx.ReadTimeout("Timeout reached")

        with pytest.raises(httpx.TimeoutException):
            fetch_post_page(2, 3)


def test_fetch_all_posts_returns_expected_data():

    with patch("api_client.fetch_post_page") as mock_page:
        mock_page.side_effect = [
            [{"id": 1}, {"id": 2}],
            [{"id": 3}, {"id": 4}],
            [{"id": 5}],
        ]
        result = fetch_all_posts(2)

    assert mock_page.call_count == 3
    assert result == [
        {"id": 1},
        {"id": 2},
        {"id": 3},
        {"id": 4},
        {"id": 5},
    ]
    assert mock_page.call_args_list == [
        call(1, 2),
        call(2, 2),
        call(3, 2),
    ]


def test_fetch_all_posts_raises_on_http_error():
    request = httpx.Request(method="GET", url="test")
    response = httpx.Response(status_code=500, request=request)
    with patch("api_client.fetch_post_page") as mock_page:
        mock_page.side_effect = [
            [{"id": 1}, {"id": 2}],
            httpx.HTTPStatusError(
                message="Error 500", request=request, response=response
            ),
        ]
        with pytest.raises(httpx.HTTPStatusError):
            fetch_all_posts(2)
        assert mock_page.call_count == 2


def test_fetch_all_posts_raises_on_timeout():
    with patch("api_client.fetch_post_page") as mock_page:
        mock_page.side_effect = [
            [{"id": 1}, {"id": 2}],
            httpx.ReadTimeout("Timeout Reached"),
            [{"id": 3}, {"id": 4}],
        ]
        with pytest.raises(httpx.TimeoutException):
            fetch_all_posts(2)
        assert mock_page.call_count == 2


def test_fetch_post_page_with_retry_succedes_on_second_attempt():
    expected_data = [{"id": 1}, {"id": 2}]
    with patch("api_client.fetch_post_page") as mock_page:
        with patch("api_client.time.sleep") as mock_sleep:
            mock_page.side_effect = [
                httpx.ReadTimeout("TimeoutReached"),
                [{"id": 1}, {"id": 2}],
            ]
            data = fetch_post_page_with_retry(page=1, limit=2)
            assert mock_page.call_count == 2
            mock_sleep.assert_called_once_with(1)
            assert mock_page.call_args_list == [call(1, 2), call(1, 2)]
            assert data == expected_data


def test_fetch_post_page_with_retry_raises_after_three_failed_timeouts():
    with patch("api_client.fetch_post_page") as mock_page:
        with patch("api_client.time.sleep") as mock_sleep:
            mock_page.side_effect = [
                httpx.ReadTimeout("TimeoutReached"),
                httpx.ReadTimeout("TimeoutReached"),
                httpx.ReadTimeout("TimeoutReached"),
            ]
            with pytest.raises(httpx.TimeoutException):
                fetch_post_page_with_retry(page=1, limit=2)
            assert mock_page.call_count == 3
            assert mock_page.call_args_list == [call(1, 2), call(1, 2), call(1, 2)]
            assert mock_sleep.call_count == 2
            assert mock_sleep.call_args_list == [call(1), call(2)]


def test_fetch_post_page_with_retry_succedes_on_first_attempt():
    expected_data = [{"id": 1}, {"id": 2}]
    with patch("api_client.fetch_post_page") as mock_page:
        with patch("api_client.time.sleep") as mock_sleep:
            mock_page.side_effect = [[{"id": 1}, {"id": 2}]]
            data = fetch_post_page_with_retry(1, 2)

            assert data == expected_data
            mock_page.assert_called_once_with(1, 2)
            mock_sleep.assert_not_called()


def test_fetch_post_page_with_retry_raises_on_http_404():
    request = httpx.Request(method="GET", url="test")
    response = httpx.Response(status_code=404, request=request)
    with patch("api_client.fetch_post_page") as mock_page:
        with patch("api_client.time.sleep") as mock_sleep:
            mock_page.side_effect = httpx.HTTPStatusError(
                message="Erorr 404", request=request, response=response
            )
            with pytest.raises(httpx.HTTPStatusError):
                fetch_post_page_with_retry(1, 2)
            mock_page.assert_called_once_with(1, 2)
            mock_sleep.assert_not_called()


def test_fetch_post_page_retry_raises_on_three_http_500():
    request = httpx.Request(method="GET", url="test")
    response = httpx.Response(status_code=500, request=request)
    error_500 = httpx.HTTPStatusError(
        message="Error 500", response=response, request=request
    )
    with patch("api_client.fetch_post_page") as mock_page:
        with patch("api_client.time.sleep") as mock_sleep:
            mock_page.side_effect = [error_500, error_500, error_500]
            with pytest.raises(httpx.HTTPStatusError):
                fetch_post_page_with_retry(1, 2)
            assert mock_page.call_count == 3
            assert mock_sleep.call_count == 2
            assert mock_page.call_args_list == [call(1, 2), call(1, 2), call(1, 2)]
            assert mock_sleep.call_args_list == [call(1), call(2)]


def test_fetch_post_page_with_retry_succedes_after_one_http_500():
    expected_data = [{"id": 1}, {"id": 2}]
    request = httpx.Request(method="GET", url="test")
    response = httpx.Response(status_code=500, request=request)
    error_500 = httpx.HTTPStatusError(
        message="Error 500", response=response, request=request
    )
    with patch("api_client.fetch_post_page") as mock_page:
        with patch("api_client.time.sleep") as mock_sleep:
            mock_page.side_effect = [error_500, [{"id": 1}, {"id": 2}]]
            data = fetch_post_page_with_retry(1, 2)
            assert data == expected_data
            assert mock_page.call_count == 2
            assert mock_page.call_args_list == [call(1, 2), call(1, 2)]
            mock_sleep.assert_called_once_with(1)


def test_fetch_post_page_retry_succedes_after_mixed_errors():
    expected_data = [{"id": 1}, {"id": 2}]
    request = httpx.Request(method="GET", url="test")
    response = httpx.Response(status_code=500, request=request)
    error_500 = httpx.HTTPStatusError(
        message="Erorr 500", request=request, response=response
    )
    with patch("api_client.fetch_post_page") as mock_page:
        with patch("api_client.time.sleep") as mock_sleep:
            mock_page.side_effect = [
                httpx.ReadTimeout("Timeaout Reached"),
                error_500,
                [{"id": 1}, {"id": 2}],
            ]
            data = fetch_post_page_with_retry(1, 2)
            assert data == expected_data
            assert mock_page.call_count == 3
            assert mock_page.call_args_list == [call(1, 2), call(1, 2), call(1, 2)]
            assert mock_sleep.call_count == 2
            assert mock_sleep.call_args_list == [call(1), call(2)]


def test_fetch_post_page_with_retry_reads_retry_after_time_from_server():
    request = httpx.Request(method="GET", url="test")
    response = httpx.Response(
        status_code=429, request=request, headers={"Retry-After": "5"}
    )
    error_429 = httpx.HTTPStatusError(
        message="Error 429", request=request, response=response
    )
    expected_data = [{"id": 1}, {"id": 2}]
    with patch("api_client.fetch_post_page") as mock_page:
        with patch("api_client.time.sleep") as mock_sleep:
            mock_page.side_effect = [error_429, expected_data]
            data = fetch_post_page_with_retry(1, 2)
            assert data == expected_data
            assert mock_page.call_count == 2
            mock_sleep.assert_called_once_with(5)


def test_fetch_post_page_with_retry_sucedes_without_retry_after_time():
    request = httpx.Request(method="GET", url="test")
    response = httpx.Response(status_code=429, request=request)
    error_429 = httpx.HTTPStatusError(
        message="Error 429", request=request, response=response
    )
    expected_data = [{"id": 1}, {"id": 2}]
    with patch("api_client.fetch_post_page") as mock_page:
        with patch("api_client.time.sleep") as mock_sleep:
            mock_page.side_effect = [error_429, expected_data]
            data = fetch_post_page_with_retry(1, 2)
            assert data == expected_data
            assert mock_page.call_count == 2
            mock_sleep.assert_called_once_with(1)
