from api_integrations.alarms_analysis.models import AlarmAnalysisResult, EvaluationStats
from pydantic import ValidationError
import pytest


@pytest.fixture
def valid_analysis_result():
    return AlarmAnalysisResult(
        id="PLC_01",
        category="electrical",
        priority="low",
        requires_review=False,
    )


@pytest.fixture
def valid_evaluation_stats(valid_analysis_result):
    pass
