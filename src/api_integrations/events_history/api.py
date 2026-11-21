from fastapi import HTTPException, Header, Depends, Query
from api_integrations.events_history.models import EventsHistoryRequest
import os
from dotenv import load_dotenv
from api_integrations.events_history.handler import (
    process_request,
)
from api_integrations.main import app
from pydantic import ValidationError

load_dotenv()
secret = os.environ["EVENTS_API_KEY"]


def validate_history_request(
    event_id: str | None = Query(default=None),
    machine: str | None = Query(default=None),
    time_from: str | None = Query(default=None),
    time_to: str | None = Query(default=None),
    limit: int = Query(default=100),
    offset: int = Query(default=0),
) -> EventsHistoryRequest:

    try:
        return EventsHistoryRequest(
            event_id=event_id,
            machine=machine,
            time_from=time_from,
            time_to=time_to,
            limit=limit,
            offset=offset,
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=422,
            detail=e.errors(include_context=False),
        ) from e


@app.get("/events")
async def get_alarms_history(
    events_api_key: str | None = Header(
        default=None,
        alias="X-API-Key",
    ),
    request: EventsHistoryRequest = Depends(validate_history_request),
):

    if events_api_key != secret:
        raise HTTPException(status_code=401, detail="Invalid events_api_key")
    return process_request(request)
