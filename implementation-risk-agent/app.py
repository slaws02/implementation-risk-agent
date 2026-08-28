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
        "No real company or client information is used."
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

risk_tab,trend_tab,prompt_tab,evidence_tab=st.tabs(["Risk Findings","Risk Trend","How to Use","Cross-System Evidence"])

with risk_tab:
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

with trend_tab:
    st.subheader("Risk Trend")
    trend_rows = history + [{
        "date": current_date.strftime("%Y-%m-%d"),
        "score": assessment.score,
        "severity": assessment.severity,
    }]
    trend_df = pd.DataFrame(trend_rows)
    st.line_chart(trend_df.set_index("date")["score"])
    st.dataframe(trend_df, use_container_width=True, hide_index=True)

with prompt_tab:
    st.subheader("How to Use This Agent")
    st.caption("Use these prompts as starting points or adapt the framework to your implementation question.")
    st.markdown("**Prompt framework:** Review **[scope]** + compare **[sources]** + identify **[risk/question]** + prioritize by **[business impact]** + show **[evidence]** + recommend **[next action/owner]**.")
    prompts=[
        "Review this implementation and tell me the three issues most likely to affect the planned launch date. Show the evidence supporting each issue.",
        "Compare the current project status across the CRM, project tracker, collaboration messages, and calendar. Identify any places where the systems tell a different story about launch readiness.",
        "Which open dependencies are most likely to become launch blockers within the next two weeks? Rank them by urgency and recommend the next action and owner.",
        "The launch risk has increased. Explain what changed since the previous assessment, which source caused the change, and what could reduce the risk score.",
        "Separate current risks into client-owned risks, internal risks, technical dependencies, and issues that need leadership escalation. Do not escalate anything that can still be resolved within the working team.",
        "Assume we cannot move the launch date. Reassess the current risks and give me the smallest set of actions that would most improve launch confidence, including owners, dependencies, and what evidence I should require before marking each issue resolved.",
    ]
    for i,p in enumerate(prompts,1): st.markdown(f"**{i}.** {p}")
    st.info("Tip: stronger questions name the scope, systems to compare, business constraint, decision needed, evidence required, and desired owner/action.")
    st.warning("Human review: verify source freshness, ownership, escalation need, and evidence before marking a risk resolved.")

with evidence_tab:
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
