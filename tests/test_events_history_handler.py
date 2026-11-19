from api_integrations.events_history.handler import process_request
from api_integrations.models import (
    RegisteredEvent,
    EventsHistoryRequest,
    AlarmData,
)
from unittest.mock import patch, call
from datetime import datetime
from zoneinfo import ZoneInfo


def test_events_history_hanlder_with_params(valid_history_request):
    expected_events = RegisteredEvent(
        event_id="evt_001",
        event="alarm.created",
        timestamp="2026-11-17T16:19:30+00:00",
        data=AlarmData(machine="PLC_01", alarm_code=204),
        received_at="2026-11-17T16:19:30+00:00",
    )
    request = valid_history_request
    request.offset = 2
    with patch(
        "api_integrations.events_history.handler.EventsRepository"
    ) as mock_repository_class:
        mock_repository = mock_repository_class.return_value
        mock_repository.get_events.return_value = expected_events, 1

        results, total = process_request(request)
        assert results == expected_events
        mock_repository.get_events.assert_called_once_with(
            event_id="evt_001",
            machine="PLC_01",
            time_from=datetime(2026, 11, 17, 16, 19, 20, tzinfo=ZoneInfo("UTC")),
            time_to=datetime(2026, 11, 17, 16, 19, 30, tzinfo=ZoneInfo("UTC")),
            limit=10,
            offset=2,
        )


def test_events_handler_with_no_time_params():
    request = EventsHistoryRequest(
        event_id=None,
        machine=None,
        time_from=None,
        time_to=None,
        limit=10,
    )
    with patch(
        "api_integrations.events_history.handler.EventsRepository"
    ) as mock_repository_class:
        mock_repository = mock_repository_class.return_value
        mock_repository.get_events.return_value = [[], 0]
        results = process_request(request)
        assert results == ([], 0)
        mock_repository.get_events.assert_called_once_with(
            event_id=None,
            machine=None,
            time_from=None,
            time_to=None,
            limit=10,
            offset=0,
        )
