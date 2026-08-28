# Launch Risk Detection Agent — Prompt Tip Sheet

## Start here
Use the agent to help you **find, compare, prioritize, and explain implementation risk**. It should support your judgment, not replace it.

### A simple prompt framework
**Review [scope] + compare [sources] + identify [risk/question] + prioritize by [business impact] + show [evidence] + recommend [next action/owner].**

Example:
> Review the current implementation across the CRM, project tracker, collaboration messages, and calendar. Identify the three issues most likely to affect launch, rank them by urgency, show the evidence, and recommend the next action and owner.

## Six prompts to try

1. **Launch risk review**  
   Review this implementation and tell me the three issues most likely to affect the planned launch date. Show the evidence supporting each issue.

2. **Cross-system consistency check**  
   Compare the current project status across the CRM, project tracker, collaboration messages, and calendar. Identify any places where the systems tell a different story about launch readiness.

3. **Forward-looking dependencies**  
   Which open dependencies are most likely to become launch blockers within the next two weeks? Rank them by urgency and recommend the next action and owner.

4. **Explain the risk change**  
   The launch risk has increased. Explain what changed since the previous assessment, which source caused the change, and what could reduce the risk score.

5. **Prepare an internal risk review**  
   Separate current risks into client-owned risks, internal risks, technical dependencies, and issues that need leadership escalation. Do not escalate anything that can still be resolved within the working team.

6. **Scenario planning**  
   Assume we cannot move the launch date. Reassess the current risks and give me the smallest set of actions that would most improve launch confidence, including owners, dependencies, and what evidence I should require before marking each issue resolved.

## Stronger questions usually include
- the implementation scope you want reviewed;
- the systems or evidence you want compared;
- the business constraint, such as a fixed launch date;
- the decision you are trying to make;
- the evidence you want returned;
- the owner or next action you need.

### Less useful
> What are the risks?

### Better
> Review the current implementation across all available sources, identify the three highest-impact risks to the November launch, explain the evidence for each, and recommend the next action and accountable owner.

## Human review checklist
Before acting on the output, confirm:
- the evidence matches the underlying source;
- an apparent conflict is not simply stale data;
- the suggested owner is appropriate;
- escalation is actually necessary;
- a risk is not marked resolved until the required evidence exists.

**The agent recommends. The implementation manager decides.**
