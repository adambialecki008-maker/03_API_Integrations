from fastapi import HTTPException, Header, Depends
from api_integrations.models import EventsHistoryRequest
import os
from dotenv import load_dotenv
from api_integrations.events_history.events_history_handler import (
    process_request,
)
from api_integrations.main import app

load_dotenv()
secret = os.environ["EVENTS_API_KEY"]


@app.get("/events")
async def get_alarms_history(
    events_api_key: str | None = Header(
        default=None,
        alias="X-API-Key",
    ),
    request: EventsHistoryRequest = Depends(),
):

    if events_api_key != secret:
        raise HTTPException(status_code=401, detail="Invalid events_Api_key")

    return process_request(request)
