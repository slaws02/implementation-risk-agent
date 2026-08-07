# Hello Heart Launch Risk Detection Agent — Mock Demo

A portfolio/demo project showing how an Implementation Manager could use an AI-enabled workflow to detect client launch risk across Salesforce, Asana, Slack, and Calendar.

> **Important:** This is a mock implementation using synthetic data. It does not connect to Hello Heart systems or contain real client information.

## What this demonstrates

The agent:

1. Pulls the official launch date and client metadata from a Salesforce-like source.
2. Reviews Asana-like tasks, milestones, owners, dependencies, and overdue work.
3. Reviews Slack-like messages for blockers, delays, unresolved dependencies, and client/vendor issues.
4. Checks Calendar-like events for required implementation milestones.
5. Applies deterministic risk rules.
6. Adds lightweight natural-language signal detection for unstructured Slack messages.
7. Produces:
   - an overall risk score,
   - Low / Medium / High / Critical classification,
   - evidence by source,
   - recommended actions,
   - suggested owners,
   - response timeframes,
   - a risk trend.

## Why this architecture

This mock separates **deterministic project controls** from **AI interpretation**.

Deterministic checks are best for facts such as:
- overdue tasks,
- days until launch,
- missing calendar milestones,
- incomplete critical deliverables.

AI/NLP-style interpretation is best for less structured signals such as:
- "still waiting on the vendor",
- "client has not sent metadata",
- "we may miss testing",
- "blocked on credentials".

A production version could replace the mock connectors with authenticated APIs or enterprise connectors.

## Architecture

```text
Salesforce ----\
Asana ----------\
Slack ------------> Connector Layer
Calendar --------/        |
                         Normalizer
                            |
              +-------------+-------------+
              |                           |
        Deterministic Rules       Unstructured Signals
              |                           |
              +-------------+-------------+
                            |
                        Risk Engine
                            |
               Score + Severity + Evidence
                            |
                      Streamlit UI
```

## Run locally

Requires Python 3.10+.

```bash
python -m venv .venv
source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## Run tests

```bash
pytest
```

## Portfolio talking points

You can explain the demo this way:

> "I separated deterministic checks from AI interpretation. Overdue tasks, launch proximity, missing milestones, and incomplete critical deliverables are evaluated through business rules. Unstructured sources such as Slack are evaluated for contextual signals like blockers and dependencies. The results are combined into an explainable risk score, with evidence and recommended actions, while keeping the implementation manager in control of escalation and client communication."

## Production roadmap

A production version could add:

- Salesforce API / enterprise connector
- Asana API
- Slack API with scoped channel permissions
- Google Calendar API
- Google Drive / implementation-document retrieval
- LLM-based classification and summarization
- human approval gates
- persistent risk-history database
- alerts and workflow automation
- role-based access control
- audit logs
- data retention and privacy controls

## Repository contents

- `app.py` — Streamlit demo
- `risk_engine.py` — scoring and risk rules
- `connectors.py` — mock connector layer
- `models.py` — shared types
- `data/` — synthetic Salesforce, Asana, Slack, Calendar, and history data
- `tests/` — basic automated tests
- `.env.example` — placeholder for future real connectors
- `requirements.txt`

## Disclaimer

This project is for demonstration and interview preparation only. All names, dates, records, and implementation details are synthetic.
