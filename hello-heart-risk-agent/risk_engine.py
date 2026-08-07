from datetime import date, datetime
from typing import List
from models import RiskFinding, RiskAssessment


SEVERITY_ORDER = {
    "Low": 1,
    "Medium": 2,
    "High": 3,
    "Critical": 4,
}


def classify_score(score: int) -> str:
    if score >= 80:
        return "Critical"
    if score >= 60:
        return "High"
    if score >= 30:
        return "Medium"
    return "Low"


def _days_between(current_date: str, launch_date: str) -> int:
    current = datetime.strptime(current_date, "%Y-%m-%d").date()
    launch = datetime.strptime(launch_date, "%Y-%m-%d").date()
    return (launch - current).days


def _finding(
    category,
    severity,
    points,
    description,
    evidence,
    source,
    impact,
    action,
    owner,
    timeframe,
):
    return RiskFinding(
        category=category,
        severity=severity,
        points=points,
        description=description,
        evidence=evidence,
        source=source,
        impact=impact,
        recommended_action=action,
        suggested_owner=owner,
        response_timeframe=timeframe,
    )


def evaluate_asana(tasks, current_date: str, days_to_launch: int) -> List[RiskFinding]:
    findings = []
    today = datetime.strptime(current_date, "%Y-%m-%d").date()

    for task in tasks:
        due = datetime.strptime(task["due_date"], "%Y-%m-%d").date()
        overdue_days = (today - due).days
        incomplete = task["status"].lower() not in {"complete", "completed", "done"}

        if incomplete and task.get("critical") and overdue_days > 0:
            points = 25 if days_to_launch <= 10 else 18
            severity = "High" if days_to_launch <= 10 else "Medium"
            findings.append(_finding(
                "Critical task overdue",
                severity,
                points,
                f'{task["name"]} is {overdue_days} day(s) overdue.',
                f'Status={task["status"]}; due={task["due_date"]}; owner={task["owner"]}',
                "Asana",
                "A critical implementation dependency may threaten launch readiness.",
                f'Confirm recovery plan and committed completion date for "{task["name"]}".',
                task["owner"],
                "Today" if severity == "High" else "Within 1 business day",
            ))

        elif incomplete and task.get("critical") and 0 <= (due - today).days <= 3:
            findings.append(_finding(
                "Critical task approaching deadline",
                "Medium",
                10,
                f'{task["name"]} is incomplete and due within 3 days.',
                f'Status={task["status"]}; due={task["due_date"]}; owner={task["owner"]}',
                "Asana",
                "Limited schedule buffer remains for a critical dependency.",
                f'Validate that "{task["name"]}" remains on track.',
                task["owner"],
                "Within 1 business day",
            ))
    return findings


def evaluate_calendar(events, current_date: str, launch_date: str, days_to_launch: int):
    findings = []
    names = " ".join(event["title"].lower() for event in events)

    if days_to_launch <= 14 and "training" not in names:
        severity = "High" if days_to_launch <= 7 else "Medium"
        points = 15 if severity == "High" else 10
        findings.append(_finding(
            "Training milestone missing",
            severity,
            points,
            "No training event is scheduled before launch.",
            f"Launch is in {days_to_launch} day(s); no calendar event contains 'training'.",
            "Calendar",
            "Users or client stakeholders may be unprepared for go-live.",
            "Confirm training requirements and schedule the required session.",
            "Implementation Manager",
            "Today" if severity == "High" else "Within 2 business days",
        ))

    if days_to_launch <= 7 and "launch readiness" not in names:
        findings.append(_finding(
            "Launch readiness review missing",
            "High",
            15,
            "No launch readiness review is scheduled within the final week.",
            f"Launch is in {days_to_launch} day(s).",
            "Calendar",
            "Critical launch decisions may occur without a formal readiness checkpoint.",
            "Schedule a cross-functional launch readiness review.",
            "Implementation Manager",
            "Today",
        ))

    return findings


def evaluate_slack(messages, days_to_launch: int):
    """
    Lightweight mock NLP. A production version would replace this with
    an LLM classifier or enterprise AI model with permissions and auditability.
    """
    findings = []
    seen_categories = set()

    patterns = [
        (
            "vendor",
            ["waiting on", "hasn't responded", "has not responded", "vendor"],
            "Vendor dependency",
            15,
            "High" if days_to_launch <= 10 else "Medium",
            "A vendor dependency appears unresolved.",
            "A third-party dependency could delay testing or launch preparation.",
            "Escalate through Vendor Operations and obtain a committed response date.",
            "Vendor Operations",
        ),
        (
            "sso",
            ["sso", "metadata", "identity provider"],
            "SSO dependency",
            20,
            "High" if days_to_launch <= 10 else "Medium",
            "Slack contains an unresolved SSO-related dependency.",
            "Authentication configuration may not be ready for launch.",
            "Confirm missing SSO information with the client technical contact.",
            "Implementation Manager",
        ),
        (
            "blocked",
            ["blocked", "blocker", "cannot proceed", "can't proceed"],
            "Operational blocker",
            18,
            "High" if days_to_launch <= 10 else "Medium",
            "A blocker was identified in implementation communications.",
            "Dependent work may be unable to proceed.",
            "Assign an owner and resolution deadline for the blocker.",
            "Implementation Manager",
        ),
    ]

    for message in messages:
        text = message["text"].lower()
        for key, keywords, category, points, severity, desc, impact, action, owner in patterns:
            if key in seen_categories:
                continue
            if any(keyword in text for keyword in keywords):
                findings.append(_finding(
                    category,
                    severity,
                    points,
                    desc,
                    f'{message["author"]}: "{message["text"]}"',
                    "Slack",
                    impact,
                    action,
                    owner,
                    "Today" if severity == "High" else "Within 1 business day",
                ))
                seen_categories.add(key)

    return findings


def evaluate_salesforce(sf, days_to_launch: int):
    findings = []

    required = sf.get("required_fields", {})
    missing = [k for k, v in required.items() if v in (None, "", False)]

    if missing:
        severity = "High" if days_to_launch <= 10 else "Medium"
        points = min(20, 5 * len(missing))
        findings.append(_finding(
            "Missing implementation information",
            severity,
            points,
            f"{len(missing)} required Salesforce field(s) are incomplete.",
            "Missing: " + ", ".join(missing),
            "Salesforce",
            "The implementation team may be planning from incomplete source-of-record data.",
            "Validate and complete the missing implementation fields.",
            "Implementation Manager",
            "Today" if severity == "High" else "Within 2 business days",
        ))

    return findings


def deduplicate(findings: List[RiskFinding]) -> List[RiskFinding]:
    """
    Preserve evidence from multiple systems while reducing obvious double-counting.
    Example: SSO risk in Asana and Slack still appears as separate evidence,
    but score contribution is capped later.
    """
    return findings


def calculate_score(findings: List[RiskFinding], days_to_launch: int) -> int:
    score = sum(f.points for f in findings)

    # Launch proximity amplifies existing risk, but proximity alone is not a risk.
    if findings:
        if days_to_launch <= 3:
            score += 20
        elif days_to_launch <= 7:
            score += 15
        elif days_to_launch <= 10:
            score += 10

    # Keep score interpretable.
    return min(100, score)


def build_summary(severity: str, score: int, findings: List[RiskFinding], delta: int):
    if not findings:
        return "No material launch risks were detected by the current rule set."

    highest = sorted(
        findings,
        key=lambda x: (SEVERITY_ORDER[x.severity], x.points),
        reverse=True,
    )[:2]

    categories = ", ".join(f.category for f in highest)
    direction = (
        f" Risk increased {delta} point(s) from the previous assessment."
        if delta > 0
        else f" Risk decreased {abs(delta)} point(s) from the previous assessment."
        if delta < 0
        else " Risk is unchanged from the previous assessment."
    )

    return (
        f"Implementation is currently {severity.upper()} risk ({score}/100). "
        f"Primary concerns: {categories}.{direction}"
    )


def assess_risk(sf, tasks, slack, events, history, current_date: str):
    days_to_launch = _days_between(current_date, sf["launch_date"])

    findings = []
    findings.extend(evaluate_salesforce(sf, days_to_launch))
    findings.extend(evaluate_asana(tasks, current_date, days_to_launch))
    findings.extend(evaluate_slack(slack, days_to_launch))
    findings.extend(evaluate_calendar(events, current_date, sf["launch_date"], days_to_launch))

    findings = deduplicate(findings)
    score = calculate_score(findings, days_to_launch)
    severity = classify_score(score)

    previous_score = history[-1]["score"] if history else 0
    previous_severity = history[-1]["severity"] if history else "Unknown"
    delta = score - previous_score

    return RiskAssessment(
        client=sf["client_name"],
        launch_date=sf["launch_date"],
        days_to_launch=days_to_launch,
        score=score,
        severity=severity,
        findings=sorted(
            findings,
            key=lambda x: (SEVERITY_ORDER[x.severity], x.points),
            reverse=True,
        ),
        previous_score=previous_score,
        previous_severity=previous_severity,
        trend_delta=delta,
        summary=build_summary(severity, score, findings, delta),
    )
