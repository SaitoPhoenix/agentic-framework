---
name: <name of the entity>
aliases:
  - <alias 1>
  - <alias 2>
  - <...>
entity_classification: <singular classification, ex. person, project, technology/database, technology/framework, concept>
status: <lifecycle of semantic memory, new | updated | active | review-needed | archived>
created: <ISO 8601 timestamp>
last_updated: <ISO 8601 timestamp>
source_episodes: 
  - <source id, ex. 250919_EP_1>
  - <source id, ex. 250919_EP_2>
  - <...>
summary: <high-level abstract of the entity>
ambiguities:
  - <description of ambiguity>
  - <description of ambiguity>
  - <...>
relationships:
  - type: <relationship type>
    entity: <entity name>
    description: <description of the relationship>
    role: <role of the entity in the relationship>
    source: <source id, ex. 250919_EP_1>
  - type: <relationship type>
    entity: <entity name>
    description: <description of the relationship>
    role: <role of the entity in the relationship>
    source: <source id, ex. 250919_EP_1>
  - <...>
---

## <Classification Heading, use for Facts | Accomplishments | Suggestions | Preferences | Philosophies | Patterns | Approaches>

### <Topic>
- <Item content> [<source_id>]
- <Item content> [<source_id>]
- <...>

<!-- Examples:
## Facts

### Integrations
- Already integrated in the GenAI Launchpad platform [250926_EP_1]
- Provides excellent async support for handling multiple audio uploads [250926_EP_1]

### Capabilities
- Provides temporal awareness for tracking when skills were learned and experiences evolved [250919_EP_1]
- Handles incremental updates exactly as needed for continuous audio log processing [250919_EP_1]

## Accomplishments

### Specifications
- Created Product Specification (PS-001) defining vision, users, and requirements [250919_EP_1]
- Created Architecture Specification (AS-001) with event-driven microservices design [250919_EP_1]

## Suggestions

### Technology Choices
- Use PydanticAI for the new LLM integration [250926_EP_1]

### Testing Processes
- Test the new LLM integration with the new feature [250926_EP_1]

## Preferences

### Architectural
- Prefers self-hosted solutions when simple (like Docker containers for Whisper) [250919_EP_1]
- Favor monolithic repositories (monorepos) for related projects to simplify dependency management and cross-project refactoring [250919_EP_1]
- Prefers combining libraries like Tremor + React Flow rather than all-in-one solutions [250919_EP_1]

### Tooling
- Prefers using uv for Python backend dependency management [EP:250919_EP_1]
- Prefers using pnpm for frontend package management [EP:250919_EP_1]

## Philosophies

### Technology Strategy
- Believes in leveraging existing platforms rather than building from scratch [250919_EP_1]

### Software Design
- Values simplicity and maintainability in technology choices [250919_EP_1]

### Communication Strategy
- Values clear documentation where non-technical people can understand architectural decisions [250919_EP_1]

## Patterns

### Expert Consultation Strategy
- Identifies appropriate domain experts based on project requirements and creates parallel consultation tasks [EP:250919_EP_1]
- Combines inputs from multiple experts into coherent, implementable system designs [EP:250919_EP_1]

### High-Level Focus
- Maintains architectural perspective, avoiding code examples and staying at system design level [EP:250919_EP_1]

## Approaches

### Approval Process
- Reviews specifications thoroughly and requests improvements for clarity before approving (e.g., requesting more verbose ADRs, adding role columns to tech stack tables) [EP:250919_EP_1]
- Prefers decisions with clear reasoning, especially for non-technical stakeholders [EP:250919_EP_1]

-->

## <Classification Heading, use for Actions | Decisions | Requirements | Constraints>

- **<Item Title>** [<source_id>]
  - **Key:** <Value>
  - **Another-Key:** <Value>
  - <...>

<!-- Required Keys:

Actions:
  - Priority # Critical, High, Medium, Low, None
  - Owner # Name of the person responsible for the action
  - Status # Not Started, Blocked, In Progress, Done
  - Description # Description of the action
  - Created # YYYY-MM-DD
  - Due # YYYY-MM-DD (set to none if not provided)

Decisions:
  - Category # Grouping for similar decisions and area of impact
  - Status # Open, Final, Archived
  - Created # YYYY-MM-DD
  - Rationale # Reasoning for the decision
  - Impact # Describe areas that are affected by the decision

Requirements:
  - Category # Grouping for similar requirements and area of impact
  - Priority # Critical, High, Medium, Low
  - Status # Open, Fulfilled, Rejected
  - Details # Description of the requirement
  - Created # YYYY-MM-DD
  
Constraints:
  - Category # Grouping for similar constraints and area of impact
  - Status # Active, Inactive
  - Scope # Describe the scope of the constraint
  - Reason # Reasoning for the constraint
  - Created # YYYY-MM-DD
-->

<!-- Examples:
## Decisions

- **Preferred Framework: PydanticAI over LangChain** [250926_EP_1]
  - **Category:** Technology Choices
  - **Status:** Final
  - **Date:** 2025-09-19
  - **Rationale:** Simpler API, superior type safety, and a smaller dependency footprint
  - **Impact:** More controlled and predictable behavior

- **Primary Communication Tool: Slack over Microsoft Teams** [250620_IT_EVAL_7]
  - **Category:** Communication Tools
  - **Status:** Archived
  - **Date:** 2025-06-20
  - **Rationale:** At the time, Slack offered a superior user experience and a more extensive ecosystem of app integrations
  - **Impact:** Not in line with our current communication tools

## Actions

- **Task: Document the new integration with Graphiti** [250927_MEET_3]
  - **Priority:** High (other priorities: Med, Low, Undefined)
  - **Owner:** George Miller
  - **Status:** Not Started (other statuses: Blocked, In Progress, Done)
  - **Blocker:** None
  - **Description:** Document the new integration with Graphiti
  - **Created:** 2025-09-27
  - **Due:** 2025-10-04 (set to none if not provided)

- **Task: Evaluate three alternative data visualization libraries for the new dashboard** [250927_FE_GUILD_4]
  - **Priority:** High (other priorities: Med, Low, Undefined)
  - **Owner:** Frontend Team
  - **Status:** Blocked (other statuses: Not Started, In Progress, Done)
  - **Blocker:** Awaiting final requirements from the Product team
  - **Description:** Evaluate three alternative data visualization libraries for the new dashboard
  - **Created:** 2025-09-27
  - **Due:** 2025-10-24 (set to none if not provided)

## Constraints

- **Backend Language: We must use Python 3.12** [250927_MEET_3]
  - **Category:** Technology Constraints
  - **Status:** Active
  - **Scope:** All backend services
  - **Reason:** Python 3.12 is the most compatible version of Python and is the only version that supports the features we need

- **Package Licensing: Must use MIT or Apache 2.0 licenses** [250701_OSS_POLICY_1]
  - **Category:** Legal/Compliance Constraints
  - **Status:** Active
  - **Scope:** All third-party software dependencies
  - **Reason:** To avoid the legal complexities and obligations associated with more restrictive licenses like GPL

## Requirements

- **Requirement: Users must be able to reset their password via email** [250815_PROD_SPEC_1]
  - **Category:** Functional
  - **Priority:** Critical
  - **Status:** Fulfilled
  - **Details:** The system must send a unique, single-use link to the user's registered email address that allows them to set a new password

- **Requirement: The checkout process must not exceed three steps** [250801_UX_STUDY_5]
  - **Category:** User Experience
  - **Priority:** High
  - **Status:** Active
  - **Details:** To reduce cart abandonment, the user journey from "Add to Cart" to "Purchase Complete" must be streamlined
-->