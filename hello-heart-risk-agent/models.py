from dataclasses import dataclass, field
from typing import List


@dataclass
class RiskFinding:
    category: str
    severity: str
    points: int
    description: str
    evidence: str
    source: str
    impact: str
    recommended_action: str
    suggested_owner: str
    response_timeframe: str


@dataclass
class RiskAssessment:
    client: str
    launch_date: str
    days_to_launch: int
    score: int
    severity: str
    findings: List[RiskFinding] = field(default_factory=list)
    previous_score: int = 0
    previous_severity: str = "Unknown"
    trend_delta: int = 0
    summary: str = ""
