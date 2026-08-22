# AI Tool Usage

## Overview

AI-assisted development was used throughout this project to accelerate implementation, explore design alternatives, debug issues, and improve documentation. AI was treated as an engineering productivity tool rather than a replacement for software design or business logic.

---

# Primary Tool Used

## ChatGPT (OpenAI)

ChatGPT was the primary AI development assistant used during the project.

It was used for:

- discussing possible system architectures before implementation
- refining the agent orchestration workflow
- generating initial code scaffolding for modules and services
- debugging Python, Streamlit and Git-related issues
- identifying edge cases during implementation
- generating unit test ideas for important business scenarios
- refining the UI structure and interaction flow
- improving code organisation and modularity
- preparing project documentation
- reviewing implementation trade-offs

---

# How AI Was Used

AI assistance was primarily used during the following stages:

### Planning

Before writing code, ChatGPT was used to discuss:

- project architecture
- folder structure
- service boundaries
- tool separation
- overall implementation strategy

---

### Development

During implementation, ChatGPT assisted with:

- boilerplate generation
- helper functions
- debugging runtime errors
- Streamlit UI refinement
- CSS improvements
- test case generation
- repository organisation

All generated code was reviewed, modified where necessary and integrated manually.

---

### Debugging

During development, ChatGPT helped troubleshoot issues including:

- Python dependency problems
- UTF-8 encoding issues
- Streamlit rendering behaviour
- Git branching and merge conflicts
- test failures
- deployment issues
- UI styling adjustments

---

### Documentation

ChatGPT assisted in preparing:

- README
- Architecture Note
- Product Note
- AI Tool Usage document
- demo video outline

The final documents were reviewed and edited before submission.

---

# Engineering Decisions Made Manually

The following project decisions were implemented manually and were not delegated to AI:

- interpreting the ParcelPilot assessment requirements
- organising the repository structure
- mapping the supplied dataset into application models
- implementing account-level access restrictions
- implementing source authority rules
- implementing deterministic cancellation and service-credit logic
- implementing ticket severity and SLA calculations
- testing the application locally
- deploying the application
- validating behaviour against the supplied dataset

---

# Development Philosophy

AI was used to improve development speed and reduce repetitive work.

Business-critical behaviour such as policy decisions, access control, financial calculations, SLA evaluation and operational workflows were implemented as explicit deterministic application logic so that the system remains predictable, explainable and testable.