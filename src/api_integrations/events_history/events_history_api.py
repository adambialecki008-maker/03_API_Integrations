from fastapi import FastAPI, HTTPException, Query, Header
from datetime import datetime
from api_integrations.events_repository import EventsRepository
from api_integrations.models import EventsHistoryRequest, TimestampUTC
import os
from dotenv import load_dotenv
from api_integrations.events_history.events_history_handler import (
    process_request,
)

app = FastAPI()
load_dotenv()
secret = os.environ["EVENTS_API_KEY"]


@app.get("/events")
async def get_alarms_history(
    events_api_key: str | None = Header(
        default=None,
        alias="X-API-Key",
    ),
    event_id: str | None = Query(default=None),
    machine: str | None = Query(default=None),
    time_from: str | None = Query(default=None),
    time_to: str | None = Query(default=None),
    limit: int | None = Query(default=100),
):

    if events_api_key != secret:
        raise HTTPException(status_code=401, detail="Invalid events_Api_key")
    try:
        request = EventsHistoryRequest(
            event_id=event_id,
            machine=machine,
            time_from=TimestampUTC(timestamp=time_from),
            time_to=TimestampUTC(timestamp=time_to),
            limit=limit,
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail="Invalid request data")
    return process_request(request)
