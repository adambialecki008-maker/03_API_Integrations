import json
from pathlib import Path
from api_integrations.alarms_analysis.models import AlarmNoteAnalysis, AlarmNoteRequest


def evaluation_runner():
    ROOT = Path(__file__).resolve().parent
    file_path = ROOT / "alarm_cases.json"
    with open(file_path, "r", encoding="utf-8") as file:
        data_list = json.load(file)
        for data in data_list:
            note = data["note"]
            del data["note"]
            print(data)
        return data_list
