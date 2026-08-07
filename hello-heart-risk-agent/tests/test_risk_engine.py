from risk_engine import classify_score, assess_risk


def test_score_classification():
    assert classify_score(0) == "Low"
    assert classify_score(29) == "Low"
    assert classify_score(30) == "Medium"
    assert classify_score(59) == "Medium"
    assert classify_score(60) == "High"
    assert classify_score(79) == "High"
    assert classify_score(80) == "Critical"


def test_mock_scenario_is_high_or_critical():
    sf = {
        "client_name": "Test Client",
        "launch_date": "2026-09-15",
        "required_fields": {"sso_metadata_received": False},
    }
    tasks = [{
        "name": "SSO Configuration",
        "owner": "Engineering",
        "due_date": "2026-09-03",
        "status": "In Progress",
        "critical": True,
    }]
    slack = [{
        "author": "Engineering",
        "text": "We are blocked and still waiting on the vendor.",
    }]
    events = []
    history = [{"date": "2026-09-06", "score": 40, "severity": "Medium"}]

    result = assess_risk(
        sf, tasks, slack, events, history, current_date="2026-09-07"
    )

    assert result.score >= 60
    assert result.severity in {"High", "Critical"}
    assert len(result.findings) >= 3
