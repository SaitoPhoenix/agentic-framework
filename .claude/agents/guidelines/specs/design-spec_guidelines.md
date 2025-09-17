## Guidelines for Writing a Design Specification (DS)

A Design Specification (DS) is a detailed, actionable plan for implementing a single feature. It translates a requirement from the Product Spec into a concrete engineering blueprint, defining the technical approach and the criteria for success before any code is written.

### The Golden Rule: Translate a Requirement into an Actionable Plan
The purpose of this document is to be self-contained and precise. A developer should be able to read the referenced user story for context, and then use this document alone to build, test, and deliver the feature. **Focus on clarity, detail, and testability for a single, well-defined feature.**

### Content & Structure Checklist

Your Design Specification should contain everything needed to implement and validate one feature.

#### ✅ Do Include:
* **A Direct Link to the Product Spec:** Always reference the specific user story or feature ID (e.g., `F-04`) from the Product Spec that this design fulfills.
* **A Concise Feature Overview:** Briefly describe the feature's purpose and the problem it solves.
* **A Focused List of Requirements:** List the 3-5 most critical functional requirements for *this feature only*.
* **A Detailed Technical Approach:** Outline the step-by-step logic, algorithm, or workflow. This should be accompanied by a visual diagram (like a flowchart).
* **Specific and Testable Acceptance Criteria:** Write clear, unambiguous success conditions using the Behavior-Driven Development (BDD) format (`GIVEN/WHEN/THEN`). These define what "done" means.
* **Constraints and Guardrails:** Call out any non-functional requirements (performance, security) and explicitly reference existing patterns from the Technology and Structure specs that must be followed.
* **A Component Interaction Diagram:** If the feature involves multiple components, services, or modules, include a diagram (like a sequence diagram) to show how they communicate.

#### ❌ Do NOT Include:
* **Scope or Requirements for Other Features:** Each feature gets its own Design Specification. Keep the focus narrow.
* **Broad Architectural or Technology Decisions:** This document should *adhere to* the existing architecture, not define it. Decisions about the project's overall tech stack belong in the Technology Spec.
* **Product-Level Justifications:** The "why" behind the feature's existence belongs in the Product Spec. This document is focused on the "how."
* **Vague or Untestable Criteria:** Avoid subjective statements. Every acceptance criterion should be a clear, verifiable outcome.

### ✍️ Guiding Principles

* **Be Self-Contained:** While linking to other specs is crucial for traceability, a developer shouldn't need to read all of them to understand how to build this feature. Provide all necessary technical details here.
* **Design for Testability:** Write the technical approach and acceptance criteria together. The design should make it straightforward to write unit, integration, and acceptance tests that validate the specified criteria.
* **Reuse Before You Build:** Before designing a new component or utility, always check the existing codebase and the Technology/Structure specs for established patterns or functions that can be reused.
* **One Feature, One Spec:** Maintain a strict one-to-one relationship between a feature and a Design Spec. If the scope feels too large for one spec, the feature might be an Epic that needs to be broken down into smaller, individual features first.

### 📊 Diagramming Guidelines

Visuals are critical in a Design Spec to show flow and interaction.

* **Use a Flowchart for the Technical Approach:** A simple flowchart or activity diagram is perfect for visualizing the overall logic, steps, and decision points of an algorithm or process.
* **Use a Sequence Diagram for Interactions:** A sequence diagram is the ideal choice for showing the messages passed between different components, services, or APIs over time. It clearly illustrates the order of operations and communication patterns.
* **Keep Diagrams Focused:** The diagram should only illustrate the process for the feature being designed. Do not include unrelated system components.