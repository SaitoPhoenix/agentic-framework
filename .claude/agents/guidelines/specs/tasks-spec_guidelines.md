## Guidelines for Writing a Tasks Specification (TS)

A Tasks Specification (TS) is the most granular document in the development process. It translates a single Design Specification into an atomic, step-by-step implementation plan. This is the final blueprint used by developers—human or AI—to write and validate the code.

### The Golden Rule: Define the Exact Steps to Implementation
The purpose of this document is to eliminate all ambiguity and guesswork before coding begins. Every task should be broken down into clear, verifiable actions. A developer should be able to execute the plan without needing to refer back to higher-level documents for technical details.

### Content & Structure Checklist

Your Task Specification must be a self-contained and actionable plan.

#### ✅ Do Include:
* **YAML Frontmatter:** All structured metadata must be in the YAML block at the top. This includes the list of tasks with their IDs, status, scope, dependencies, and purpose.
* **A Complete Task List:** Break down the feature into the smallest logical and completable units of work.
* **Explicit Agent Roles:** For an agentic workflow, the `agents_involved` field must be clearly defined for each task.
* **Markdown Body:** The narrative context, detailed step-by-step instructions, and supporting diagrams belong in the Markdown section.
* **Visual Execution Order:** Always include a diagram (like the provided Mermaid graph) to visually represent task dependencies.
* **A Clear Definition of Done:** The `Success Criteria` section must provide a definitive checklist for when the entire feature is complete.
* **Full Traceability:** Ensure the `design_spec_ref` is correct at the start and the `implementation_link` is filled out for each task upon completion.

#### ❌ Do NOT Include:
* **New Requirements:** All requirements must originate from the Product Spec and be defined in the Design Spec. This document is for implementation only.
* **High-Level Design Decisions:** Architectural choices and major technical approaches are decided in the Design Spec. This document details the *execution* of that design.
* **Ambiguous Instructions:** Avoid vague phrases like "implement the backend." Be specific: "Create a new endpoint at `POST /api/transactions` that accepts a JSON body..."
* **Scope Creep:** The tasks defined must not go beyond the scope and acceptance criteria laid out in the parent Design Spec.

### ✍️ Guiding Principles

* **Atomicity:** Each task should represent a single, logical piece of work that can be completed, tested, and reviewed independently. If a task feels too large or has multiple distinct parts, break it down further.
* **Clarity for Agents:** Write instructions with the precision required for an AI agent. Be explicit about function names, required parameters, and expected outcomes.
* **Keep YAML and Markdown in Sync:** This is the most critical discipline for this format. The task `id` and `name` in the YAML frontmatter **must** match the corresponding headers in the Markdown body.
* **Maintain the Linkage:** Traceability is key. The spec links the *design* to the *tasks*, and the tasks are then linked to the final *code* via the implementation links. This creates a fully connected audit trail.

### 📝 Writing Effective Instructions (Good vs. Bad Examples)

The quality of your instructions directly impacts the quality and speed of implementation. Be explicit, especially when writing for AI agents.

#### Example 1: Backend Service Creation

* **Bad Instruction 👎**
    * Implement the categorization service.
    * *(**Why it's bad:** This is too high-level. It doesn't specify the location, method signatures, or the logic to be implemented. It assumes too much context.)*

* **Good Instruction 👍**
    * - Create a new file: `src/services/categorization.py`
    * - Define a class: `CategorizationService`
    * - Add method: `categorize(description: str) -> str`
    * - Implement simple logic: return 'Food' if 'coffee' in description.

#### Example 2: Database Migration

* **Bad Instruction 👎**
    * Update the database for categories.
    * *(**Why it's bad:** Ambiguous. Doesn't state which table, what fields, what data types, or how the change should be applied via a migration.)*

* **Good Instruction 👍**
    * - Add a new nullable field `category_id` (Integer) to the `transactions` table.
    * - Create a new database migration script to apply this change.
    * - Add a foreign key constraint to the `categories` table.

#### Example 3: UI Component Update

* **Bad Instruction 👎**
    * Show the category in the UI.
    * *(**Why it's bad:** Lacks detail. Doesn't specify the component, the location within it, the styling, or how to handle edge cases like a missing category.)*

* **Good Instruction 👍**
    * - In `TransactionListItem.tsx`, display the category name below the transaction amount.
    * - Use the `<Badge>` component for styling.
    * - If the category is null, render nothing.

### ⚙️ Workflow Integration

* **The Final Checkpoint:** This specification should be the final artifact reviewed and approved by a technical lead before implementation begins. It serves as the definitive agreement on "how we will build this."
* **A Living Progress Tracker:** This is not a "fire-and-forget" document. The `status` and `implementation_link` fields should be actively updated as work progresses. It becomes a real-time record of the feature's development.
* **The Agent's Source of Truth:** In your agentic process, the YAML frontmatter is the primary input for the Team Leader Agent to orchestrate work. Its accuracy and structure are paramount.
