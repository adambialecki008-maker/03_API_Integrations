from api_integrations.models import EventsHistoryRequest, RegisteredEvent
from api_integrations.events_repository import EventsRepository
from datetime import datetime


def process_request(request: EventsHistoryRequest) -> tuple[list[RegisteredEvent], int]:
    event_id = request.event_id
    machine = request.machine
    time_from = (
        datetime.fromisoformat(request.time_from)
        if request.time_from is not None
        else None
    )
    time_to = (
        datetime.fromisoformat(request.time_to) if request.time_to is not None else None
    )
    limit = request.limit
    offset = request.offset
    repository = EventsRepository()

    results, total = repository.get_events(
        event_id=event_id,
        machine=machine,
        time_from=time_from,
        time_to=time_to,
        limit=limit,
        offset=offset,
    )

    return results, total
