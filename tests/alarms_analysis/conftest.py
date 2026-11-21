from api_integrations.alarms_analysis.models import AlarmNoteAnalysis
import pytest


@pytest.fixture
def valid_alarm_note():
    return AlarmNoteAnalysis(
        category="electrical",
        priority="high",
        summary="Test sumamry",
        evidence=["ev_1", "ev_2", "ev_3"],
        requires_review=False,
    )
