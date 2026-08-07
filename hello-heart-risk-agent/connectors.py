import json
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"


def _load(name: str):
    with open(DATA_DIR / name, "r", encoding="utf-8") as f:
        return json.load(f)


def get_salesforce_record():
    """Mock Salesforce connector."""
    return _load("salesforce.json")


def get_asana_tasks():
    """Mock Asana connector."""
    return _load("asana.json")


def get_slack_messages():
    """Mock Slack connector."""
    return _load("slack.json")


def get_calendar_events():
    """Mock Google Calendar connector."""
    return _load("calendar.json")


def get_risk_history():
    """Mock persistent risk history."""
    return _load("risk_history.json")
