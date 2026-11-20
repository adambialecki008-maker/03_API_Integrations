from fastapi import Header, Query, HTTPException
from api_integrations.main import app
from dotenv import load_dotenv
import os, httpx, ollama
from api_integrations.alarms_analysis.models import AlarmNoteAnalysis, AlarmNoteRequest
from api_integrations.alarms_analysis.analyzer import analyze_alarm_note
from pydantic import ValidationError

load_dotenv()
secret = os.environ["ANALYZE_OPERATOR_NOTE_API_KEY"]


@app.post("/analyze_note")
def post_analyzed_note(
    request: AlarmNoteRequest,
    analyze_api_key: str | None = Header(
        default=None,
        alias="X-API-Key",
    ),
) -> AlarmNoteAnalysis:
    if analyze_api_key != secret:
        raise HTTPException(status_code=401, detail="Invalid analzye_api_key")
    try:
        result = analyze_alarm_note(request.note)
    except ValidationError as e:
        raise HTTPException(
            status_code=422,
            detail=f"LLM response validation failed: {e}",
        ) from e
    except ValueError as e:
        raise HTTPException(
            status_code=502,
            detail=f"Invalid LLM evidence: {e}",
        ) from e
    except httpx.TimeoutException as e:
        raise HTTPException(
            status_code=504,
            detail="Ollama request timed out",
        ) from e
    except ConnectionError as e:
        raise HTTPException(
            status_code=503,
            detail="Ollama service unavailable",
        ) from e
    except ollama.ResponseError as e:
        raise HTTPException(
            status_code=502,
            detail=f"Ollama response error: {e}",
        ) from e
    return result
