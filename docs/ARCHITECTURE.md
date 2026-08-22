# ParcelPilot Control Desk — Architecture Note

## 1. System Overview

ParcelPilot Control Desk is a source-aware support and operations application built for two user contexts:

* Customer-facing support
* Internal support and operations

The system combines natural-language request handling, structured operational data, document retrieval, deterministic business rules, access control, and confirmation-gated operational actions.

The application is designed around a central orchestrator that receives a user request, identifies the request type, selects the required tools, applies account and role restrictions, and returns an answer with evidence, warnings, confidence, and visible tool activity.

The architecture is intentionally lightweight because the supplied dataset is small and static. The same design can later be extended to a production environment with enterprise identity, persistent databases, semantic retrieval, external support systems, and monitoring.

## 2. High-Level Architecture

```text
User
  |
  v
Streamlit Interface
  |
  v
Role and Account Context
  |
  v
ParcelPilot Agent Orchestrator
  |
  +--------------------+--------------------+--------------------+
  |                    |                    |                    |
  v                    v                    v                    v
Document Search   Structured Data      Rule Engine       Action Tool
Tool              Lookup Tool          Tools             |
  |                    |                    |              |
  v                    v                    v              v
PDF Sources       Excel Workbook       Policy Logic      Pending Action
                                                       Confirmation
                                                            |
                                                            v
                                                      Completed Action
  |
  v
Source-Aware Response
  |
  +-- Answer
  +-- Tool activity
  +-- Sources
  +-- Confidence
  +-- Warnings
  +-- Confirmation controls
```

## 3. Agent Design

### Central Orchestrator

The application uses a single central orchestrator rather than multiple independent agents.

The orchestrator is responsible for:

* Reading the natural-language request
* Extracting order, ticket, and action identifiers
* Identifying the likely intent
* Applying the active role and account context
* Selecting one or more tools
* Combining tool outputs
* Returning a structured response
* Requesting confirmation before state-changing actions

The main request types currently supported are:

* Order lookup
* Ticket lookup
* Cancellation decision
* Service-credit decision
* Ticket severity and SLA assessment
* Document search
* Escalation preparation
* Escalation confirmation or cancellation

### Why a Single Orchestrator

A multi-agent design would introduce additional routing complexity, latency, and debugging overhead without providing meaningful value for the small assessment dataset.

A single orchestrator provides:

* Predictable control flow
* Easier testing
* Lower deployment complexity
* Clear access-control enforcement
* Transparent tool traces
* Fewer opportunities for conflicting agent decisions

The orchestrator can still invoke multiple tools within a single request.

### Multi-Step Reasoning

For a request such as:

```text
Can Northstar cancel ORD-1001 without a cancellation fee?
```

the system performs the following steps:

1. Extracts `ORD-1001`
2. Routes the request to the cancellation tool
3. Looks up the order in structured data
4. Identifies the associated account
5. Applies the Northstar customer agreement
6. Compares the agreement with the default cancellation SOP
7. Determines that the agreement overrides the default fee rule
8. Returns the decision with the relevant sources

For an escalation request, the agent first evaluates the ticket and then prepares a pending action. Execution occurs only after explicit confirmation.

## 4. Tool Design

The system exposes four main tool categories.

### Tool 1: Document Search

Purpose:

* Search current policies
* Search operating procedures
* Search product documentation
* Search customer-specific agreements
* Allow deprecated-source review only in an internal audit context

The document service loads the supplied PDFs, extracts text, attaches metadata, and ranks sources by authority.

Each document record contains:

* Document identifier
* Title
* Filename
* Document type
* Status
* Authority rank
* Account scope
* Extracted text

The document search tool filters inaccessible agreements before returning results.

### Tool 2: Structured Data Lookup

Purpose:

* Query accounts
* Query orders
* Query tickets
* Return account-linked context
* Enforce account-level privacy

The supplied Excel workbook is loaded into Pandas dataframes.

The data layer exposes explicit methods such as:

* `get_account`
* `get_order`
* `get_ticket`
* `get_account_orders`
* `get_account_tickets`

Customer access is restricted using `permitted_account_id`.

This enforcement happens inside the data service rather than relying on the language model or interface.

### Tool 3: Deterministic Rule Engine

Purpose:

* Evaluate cancellation eligibility
* Calculate cancellation fees
* Evaluate failed-pickup service credits
* Calculate credit amounts
* Determine ticket severity
* Determine applicable SLA targets
* Detect SLA breaches
* Recommend escalation

These decisions are implemented in Python.

This is important because policy-sensitive and financial outputs should be:

* Reproducible
* Testable
* Explainable
* Independent of model wording
* Protected from hallucination

Examples of explicit rules include:

* Northstar’s signed agreement overrides the standard cancellation fee
* LumenWorks uses a four-hour failed-pickup threshold and a fixed INR 300 credit
* PICKED_UP shipments use the return-to-origin workflow
* P1 incidents require immediate escalation
* Customer agreements override general policies where applicable

### Tool 4: State-Changing Action

Purpose:

* Prepare an escalation
* Require confirmation
* Create or cancel the escalation

The action tool follows a two-stage design:

1. Prepare a pending action
2. Execute only after explicit confirmation

A prepared escalation includes:

* Action ID
* Ticket ID
* Account ID
* Reason
* Requesting role
* Status
* Timestamp

The application does not execute the action when it is first requested.

Instead, the user receives:

* The prepared action ID
* A description of what will happen
* Confirm and Cancel controls

This satisfies the requirement that state-changing actions require explicit confirmation.

## 5. Document Handling

### Ingestion

The six supplied PDFs are loaded from the project’s document directory using PyPDF.

Text is extracted from each page and normalised into a single searchable string.

The documents are assigned metadata through an explicit catalog.

### Document Types

The system recognises:

* Current support policy
* Deprecated support policy
* Current cancellation and service-credit SOP
* Current product operations guide
* Northstar customer agreement
* LumenWorks customer agreement

### Document Status

Each source is marked as:

* Current
* Deprecated

Deprecated sources are excluded from ordinary search and assistant responses.

Internal users may choose to include them for audit review.

### Account Scope

Customer agreements are tagged with the relevant account ID.

Examples:

```text
Northstar agreement → ACCT-001
LumenWorks agreement → ACCT-002
```

A customer can only retrieve the agreement belonging to their active account.

Internal support users can search all authorised agreements.

### Retrieval Approach

The submitted implementation uses metadata-aware keyword retrieval.

The score considers:

* Query-term matches
* Source authority
* Account accessibility
* Current or deprecated status

The tool returns:

* Matching source
* Source authority
* Matching terms
* Relevant snippets
* Account scope
* Status

### Why Keyword Retrieval Was Used

The supplied source collection is small, structured, and domain-specific.

Using a vector database would add:

* Embedding dependencies
* Index persistence requirements
* More deployment complexity
* More failure modes
* Less transparent ranking

Keyword retrieval was therefore selected as the simpler and more reliable solution for this dataset.

For a larger production corpus, hybrid retrieval would be appropriate.

## 6. Structured-Data Handling

The supplied workbook contains:

* README metadata
* Accounts
* Orders
* Tickets

The data service loads each sheet into a Pandas dataframe.

Column names are normalised, and required sheets are validated during application startup.

The workbook snapshot time is treated as the reference time for all time-based calculations.

Structured data supports:

* Account identification
* Order status
* Booking and cancellation timing
* Pickup timing
* Carrier and customer fault
* Shipment fee
* Ticket creation time
* Ticket status
* Ticket subject and description
* Plan and support context

Historical ticket resolutions are deliberately excluded from primary decision logic because they may contain incorrect guidance.

## 7. Source Reliability and Conflict Handling

Source reliability is a core part of the design.

### Source Precedence

The application uses the following order:

1. Signed customer agreement
2. Current policy or current SOP
3. Current product documentation
4. Structured operational data
5. Historical ticket resolutions as context only
6. Deprecated sources for audit review only

### Contract Overrides

Customer-specific agreements may replace default rules.

Examples:

* Northstar’s agreement replaces the default cancellation-fee rule
* LumenWorks replaces the default failed-pickup threshold and credit amount
* Customer-specific SLA targets replace standard plan targets

### Deprecated Material

Support Policy v2 is marked as deprecated.

It is:

* Excluded from normal responses
* Excluded from default source search
* Available only when internal users explicitly enable audit review
* Assigned a low authority score

### Historical Tickets

Historical resolutions are not used as authoritative policy.

They are excluded from the main ticket view and decision logic.

### Conflict Behaviour

When authoritative facts are missing or conflicting, the system avoids promising an outcome.

Examples include:

* Unknown carrier fault
* Missing pickup timing
* Missing cancellation-request timing
* Unclear customer responsibility
* Unsupported order status

In these cases, the system:

* Reduces confidence
* Displays a warning
* Recommends human verification
* Avoids a state-changing action

## 8. Access Control and Privacy

The application supports:

* Customer context
* Support Operations context

### Customer Context

Customers can only access:

* Their account
* Their orders
* Their tickets
* Their signed agreement
* General current policies and documentation

They cannot:

* Retrieve another customer’s order
* Retrieve another customer’s ticket
* Search another customer’s agreement
* Access the Operations Radar
* Execute internal escalation actions

### Internal Context

Support Operations users can:

* Investigate all supplied accounts
* Search all authorised documents
* Access proactive operational insights
* Prepare escalations
* Confirm or cancel pending actions

### Enforcement Layer

Access restrictions are applied inside:

* Structured data tools
* Document search
* Action tools

This prevents exposure even if the interface or routing layer behaves incorrectly.

## 9. Proactive Issue Detection

The additional client problem implemented was Proactive Issue Detection.

The Operations Radar analyses open support activity and surfaces:

* P1 tickets
* SLA breaches
* Tickets requiring escalation
* Recurring issue groups
* Cross-customer issue patterns
* Known product-issue matches
* Carrier-fault signals

### Urgent Queue

Each open ticket is assessed using the rule engine.

Tickets are prioritised by:

* Escalation requirement
* P1 severity
* SLA breach
* Age

### Recurring Patterns

Ticket subjects and descriptions are scanned for issue families such as:

* Bulk upload failure
* Pickup delay
* Shipment-creation outage
* Credential exposure
* Cancellation requests

The dashboard indicates:

* Number of matching tickets
* Number of affected accounts
* Whether the issue affects multiple customers

### Known-Issue Matching

Open tickets are compared with active known issues from product documentation.

The dashboard shows:

* Ticket ID
* Matching known-issue ID
* Product-issue status
* Recommended workaround

## 10. Response Design

The agent returns a structured response containing:

* Answer
* Intent
* Success status
* Tool traces
* Sources
* Warnings
* Confidence
* Confirmation requirement
* Pending action ID
* Structured result data

The interface exposes this through:

* Main answer
* Confidence label
* Route label
* Tool activity expander
* Sources-used expander
* Warning messages
* Confirmation controls

This makes the system easier to review and reduces the risk of invisible reasoning or unsupported answers.

## 11. Testing Strategy

The project includes automated tests for:

* Workbook loading
* Required sheets
* Account lookup
* Account-scoped order access
* PDF loading
* Deprecated-source exclusion
* Agreement isolation
* Cancellation rules
* Service-credit rules
* Ticket assessment
* SLA calculations
* Escalation preparation
* Escalation confirmation
* Escalation cancellation
* Natural-language routing
* Cross-account blocking
* Proactive issue detection

The tests focus on business-critical and privacy-sensitive behaviour.

## 12. Major Technical Trade-Offs

### Streamlit Instead of Separate Frontend and Backend

Selected because:

* Faster implementation
* Single deployment
* Built-in chat interface
* Sufficient for assessment-scale usage
* Lower integration risk

Trade-off:

* Less frontend flexibility
* Not ideal for high-scale production
* UI and backend run in the same process

### Rule-Based Routing Instead of LLM Tool Calling

Selected because:

* No external API dependency
* Predictable behaviour
* Easy testing
* Zero inference cost
* Stable demo environment

Trade-off:

* Less flexible for highly varied language
* Requires explicit route patterns
* Does not provide broad conversational interpretation

A production version could combine an LLM planner with the same deterministic tools.

### Keyword Retrieval Instead of Vector Search

Selected because:

* Small source set
* Transparent matching
* Simple deployment
* No embedding cost
* Easier debugging

Trade-off:

* Weaker semantic matching
* Sensitive to wording
* Less suitable for a large corpus

### Pandas Instead of a Database

Selected because:

* Dataset is supplied as a static workbook
* Fast local filtering
* Minimal setup
* Good fit for the assessment

Trade-off:

* No concurrent writes
* No production transaction model
* Limited scalability

### JSON Action Storage Instead of External Ticket Integration

Selected because:

* State-changing behaviour can be demonstrated safely
* No external credentials required
* Confirmation workflow remains testable

Trade-off:

* Actions are mocked
* Storage is local and temporary
* No real ticketing-system update occurs

### Single Agent Instead of Multiple Agents

Selected because:

* Smaller system
* Predictable routing
* Lower latency
* Easier testing and debugging

Trade-off:

* Less specialised autonomy
* More central logic
* Future scaling may require separate planning and execution components

## 13. Production Evolution

For a production implementation, the next architecture would include:

* OAuth or enterprise SSO
* Persistent relational database
* Central audit log
* Role-based authorisation service
* Zendesk, Freshdesk, or Salesforce integration
* Carrier API integrations
* Hybrid keyword and vector retrieval
* Embedding and document-index pipeline
* LLM-based planning with guarded tool execution
* Evaluation and observability platform
* Human-review workflow
* Background SLA monitoring
* Notification integrations
* Encryption and secrets management
* Rate limiting and abuse protection

## 14. Summary

The submitted architecture prioritises:

* Reliability over unconstrained generation
* Tool-level privacy over prompt-only restrictions
* Explicit policy rules over model calculation
* Source authority over equal-source retrieval
* Human confirmation over automatic state changes
* Transparency over hidden decisions
* Simplicity over unnecessary infrastructure

The result is a compact but complete support system that demonstrates agent orchestration, multi-step tool use, structured and unstructured data handling, source conflict resolution, privacy controls, controlled actions, and proactive operational intelligence.
