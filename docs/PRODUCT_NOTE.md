# ParcelPilot Control Desk – Product Note

## Overview

ParcelPilot Control Desk was designed to help both customers and internal support teams resolve operational questions faster while maintaining reliability, transparency, and access control.

Instead of acting as a generic chatbot, the application combines structured operational data, policy documents, customer agreements, deterministic business rules, and controlled operational actions to provide trustworthy support.

---

# Additional Client Problem Chosen

## Proactive Operational Intelligence

Beyond answering support questions, I wanted to address another challenge that support organisations face:

Support teams often discover incidents only after customers report them individually.

When similar issues affect multiple customers, agents investigate each ticket separately even though they originate from the same underlying problem.

This increases response times, duplicates effort, and delays engineering escalation.

To address this, I built the **Operations Radar**, a proactive dashboard that continuously analyses open tickets and highlights situations requiring immediate attention.

The dashboard identifies:

- P1 incidents
- SLA breaches
- Tickets requiring escalation
- Recurring issue patterns
- Cross-customer issue clusters
- Known product issue matches
- Carrier-related operational signals

This allows support teams to detect operational problems before they become widespread customer escalations.

---

# How I Addressed It

The Operations Radar introduces an additional analysis layer on top of the assistant.

Instead of waiting for a user question, it evaluates the operational dataset and surfaces actionable insights.

The implementation includes:

- Automatic ticket severity assessment
- SLA breach detection
- Escalation recommendation
- Pattern detection across ticket subjects and descriptions
- Identification of issues affecting multiple customers
- Matching open tickets with known product issues
- Carrier performance indicators

The dashboard is available only to authorised internal support users.

Customers cannot access operational intelligence.

---

# Additional Features I Would Build

Given additional development time, I would extend the system with the following capabilities.

## Real Authentication

Replace the current demo role selector with enterprise authentication using SSO or OAuth together with role-based permissions.

---

## Ticketing Platform Integration

Connect directly with systems such as Zendesk, Freshdesk or Salesforce so that escalations update real support tickets instead of local JSON files.

---

## Carrier Integrations

Retrieve live shipment information from carrier APIs rather than relying only on the provided dataset.

---

## Semantic Retrieval

Introduce hybrid keyword and vector search so that policy retrieval works well even when users phrase questions differently.

---

## Continuous Monitoring

Instead of refreshing only when the application loads, background workers would continuously monitor:

- new tickets
- SLA timers
- carrier failures
- operational incidents

Support teams could receive alerts immediately.

---

## Human Feedback Loop

Allow support agents to mark responses as:

- Correct
- Partially correct
- Incorrect

This feedback could be used to improve routing, retrieval and evaluation over time.

---

## Analytics Dashboard

Add product analytics showing:

- first-contact resolution rate
- average handling time
- escalation trends
- SLA performance
- policy usage
- agreement override frequency

These metrics would help operations managers identify long-term improvements.

---

# What I Intentionally Left Out

To keep the submission focused and achievable within the assessment scope, I intentionally excluded several production-level features.

These include:

- enterprise authentication
- persistent database storage
- external ticketing integrations
- carrier API integrations
- vector database infrastructure
- cloud audit logging
- background processing
- notification services
- production monitoring
- LLM-based planning and reasoning

The current implementation focuses on demonstrating reliable system design rather than production infrastructure.

---

# Product Decisions

Several design decisions were made deliberately.

### Deterministic business logic

Financial calculations, SLA evaluation and policy decisions are implemented in Python rather than relying on generated responses.

This improves consistency, explainability and testability.

---

### Explicit confirmation for actions

State-changing actions are never executed immediately.

Users must explicitly confirm an escalation before it is created.

This reduces accidental operational changes.

---

### Source transparency

Every response exposes:

- tools used
- supporting sources
- confidence
- warnings

This helps support agents verify important decisions instead of blindly trusting the assistant.

---

### Lightweight architecture

The supplied dataset is relatively small, so introducing vector databases, orchestration frameworks or distributed infrastructure would have increased complexity without providing meaningful value for this assessment.

---

# Success Metric

The primary metric I would use to evaluate the usefulness of ParcelPilot Control Desk is:

## Correct Resolution Rate without Human Rework

This measures the percentage of assistant-supported cases that are resolved correctly without requiring another support agent to revisit or correct the decision.

Supporting metrics would include:

- First Contact Resolution (FCR)
- Average Investigation Time
- SLA Compliance
- Escalation Precision
- Customer Satisfaction (CSAT)
- Reduction in duplicate investigations

Together, these metrics would indicate whether the assistant genuinely improves operational efficiency rather than simply answering questions.

---

# Final Thoughts

The goal of this submission was not simply to build a chatbot, but to demonstrate how AI can safely support operational decision-making.

The application combines structured data, policy documents, deterministic business rules and controlled actions into a transparent workflow that prioritises reliability, privacy and explainability while remaining simple enough to extend into a production system.