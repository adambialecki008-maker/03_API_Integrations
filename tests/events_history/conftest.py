import pytest
from api_integrations.events_history.models import EventsHistoryRequest


@pytest.fixture
def valid_history_request():
    return EventsHistoryRequest(
        event_id="evt_001",
        machine="PLC_01",
        time_from="2026-11-17T16:19:20+00:00",
        time_to="2026-11-17T16:19:30+00:00",
        limit=10,
    )
