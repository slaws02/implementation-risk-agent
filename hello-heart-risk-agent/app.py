import pandas as pd
import streamlit as st

from connectors import (
    get_salesforce_record,
    get_asana_tasks,
    get_slack_messages,
    get_calendar_events,
    get_risk_history,
)
from risk_engine import assess_risk


st.set_page_config(
    page_title="Launch Risk Detection Agent",
    page_icon="⚠️",
    layout="wide",
)

st.title("Launch Risk Detection Agent")
st.caption(
    "Mock AI-enabled implementation risk workflow using synthetic "
    "Salesforce, Asana, Slack, and Calendar data."
)

with st.sidebar:
    st.header("Demo Controls")
    current_date = st.date_input(
        "Assessment date",
        value=pd.to_datetime("2026-09-07"),
    )
    st.info(
        "All data in this demo is synthetic. "
        "No real Hello Heart or client information is used."
    )

sf = get_salesforce_record()
tasks = get_asana_tasks()
slack = get_slack_messages()
events = get_calendar_events()
history = get_risk_history()

assessment = assess_risk(
    sf=sf,
    tasks=tasks,
    slack=slack,
    events=events,
    history=history,
    current_date=current_date.strftime("%Y-%m-%d"),
)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Client", assessment.client)
c2.metric("Days to Launch", assessment.days_to_launch)
c3.metric(
    "Risk Score",
    assessment.score,
    delta=assessment.trend_delta,
)
c4.metric("Risk Level", assessment.severity)

if assessment.severity == "Critical":
    st.error(assessment.summary)
elif assessment.severity == "High":
    st.warning(assessment.summary)
elif assessment.severity == "Medium":
    st.info(assessment.summary)
else:
    st.success(assessment.summary)

st.subheader("Risk Findings")

if not assessment.findings:
    st.success("No material risks detected.")
else:
    for i, finding in enumerate(assessment.findings, 1):
        with st.expander(
            f"{i}. [{finding.severity}] {finding.category} (+{finding.points})",
            expanded=(i <= 3),
        ):
            st.write(f"**Description:** {finding.description}")
            st.write(f"**Source:** {finding.source}")
            st.write(f"**Evidence:** {finding.evidence}")
            st.write(f"**Potential impact:** {finding.impact}")
            st.write(f"**Recommended action:** {finding.recommended_action}")
            st.write(f"**Suggested owner:** {finding.suggested_owner}")
            st.write(f"**Response timeframe:** {finding.response_timeframe}")

st.subheader("Risk Trend")
trend_rows = history + [{
    "date": current_date.strftime("%Y-%m-%d"),
    "score": assessment.score,
    "severity": assessment.severity,
}]
trend_df = pd.DataFrame(trend_rows)
st.line_chart(trend_df.set_index("date")["score"])
st.dataframe(trend_df, use_container_width=True, hide_index=True)

st.subheader("Cross-System Evidence")

tab1, tab2, tab3, tab4 = st.tabs(
    ["Salesforce", "Asana", "Slack", "Calendar"]
)

with tab1:
    st.json(sf)

with tab2:
    st.dataframe(pd.DataFrame(tasks), use_container_width=True, hide_index=True)

with tab3:
    st.dataframe(pd.DataFrame(slack), use_container_width=True, hide_index=True)

with tab4:
    st.dataframe(pd.DataFrame(events), use_container_width=True, hide_index=True)

st.divider()
st.caption(
    "Human-in-the-loop design: the agent recommends actions and surfaces evidence. "
    "It does not change launch dates or contact clients autonomously."
)
