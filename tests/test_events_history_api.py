from fastapi.testclient import TestClient
from api_integrations.events_history.api import app, secret
from unittest.mock import patch
import pytest, json
from api_integrations.models import EventsHistoryRequest

client = TestClient(app)


def test_get_events_returns_http_401_if_no_api_key():
    response = client.get("/events")
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid events_api_key"}


def test_get_events_returns_http_401_if_invalid_api_key():
    headers = {"X-API-Key": "invalid_key"}
    response = client.get("/events", headers=headers)
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid events_api_key"}


def test_get_events_returns_200_and_no_data_if_empty_request():
    headers = {"X-API-Key": secret}
    with patch("api_integrations.events_history.api.process_request") as mock_request:
        mock_request.return_value = []
        response = client.get("/events", headers=headers)
    assert response.status_code == 200
    assert response.json() == []


def test_get_alarms_history_returns_200_and_expected_data(valid_history_request):
    request = valid_history_request.model_dump()
    headers = {"X-API-Key": secret}

    with patch("api_integrations.events_history.api.process_request") as mock_request:
        mock_request.return_value = "what I expected "
        response = client.get("/events", headers=headers, params=request)
    assert response.status_code == 200
    assert response.json() == "what I expected "


def test_get_alarm_history_returns_http_422_on_incorrect_data_format(
    valid_history_request,
):
    headers = {"X-API-Key": secret}
    invalid_request = valid_history_request
    invalid_request.time_to = "2026-11-17T16:19:30"  # No tiemzone
    request = invalid_request.model_dump()
    response = client.get("/events", headers=headers, params=request)
    errors = response.json()["detail"]
    assert response.status_code == 422
    assert any("Value error, No timezone provided" in err["msg"] for err in errors)


def test_get_alarm_history_returns_http_422_on_reversed_data(
    valid_history_request,
):
    headers = {"X-API-Key": secret}
    invalid_request = valid_history_request
    invalid_request.time_to = "2026-11-17T16:19:30+00:00"
    invalid_request.time_from = "2026-11-17T16:19:32+00:00"
    request = invalid_request.model_dump()
    response = client.get("/events", headers=headers, params=request)
    assert response.status_code == 422


def test_get_alarm_history_returns_http_422_on_limit_out_of_bounds(
    valid_history_request,
):
    headers = {"X-API-Key": secret}
    invalid_request = valid_history_request
    invalid_request.limit = 101
    request = invalid_request.model_dump()
    response = client.get("/events", headers=headers, params=request)
    assert response.status_code == 422


def test_alarm_history_returns_http_422_on_offset_out_of_bounds(valid_history_request):
    headers = {"X-API-Key": secret}
    invalid_requaest = valid_history_request
    invalid_requaest.offset = -1
    request = invalid_requaest.model_dump()
    response = client.get("/events", headers=headers, params=request)
    assert response.status_code == 422
