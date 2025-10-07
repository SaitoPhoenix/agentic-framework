## Guidelines for Writing a Structure Specification (SS)

A Structure Specification (SS) is the blueprint for your codebase's organization. It defines the rules for where files live, what they are named, and how code is structured internally. Its goal is to create a consistent, predictable, and maintainable environment for all developers.

### The Golden Rule: Promote Consistency and Readability
The primary goal of this document is to ensure the entire codebase looks and feels as though it were written by a single person. When a developer moves between different parts of the project, the layout and patterns should be familiar. **Consistency is more important than individual preference.**

### Content & Structure Checklist

Your Structure Specification should provide a clear and comprehensive guide to the project's layout and conventions.

#### ✅ Do Include:
* **A Clear Directory Layout:** Visually map out the project's folder structure, including a brief description of each top-level directory's purpose.
* **Specific Naming Conventions:** Provide unambiguous rules for naming files, classes, functions, variables, and constants. Use examples for clarity.
* **Defined Import & Dependency Rules:** Specify the order of imports and the rules for how modules can depend on each other (e.g., absolute vs. relative paths).
* **Internal File Structure Patterns:** Define the standard layout for code within a file (e.g., imports first, then constants, then the main implementation).
* **High-Level Guiding Principles:** State the core philosophies that drive your structural decisions (e.g., Single Responsibility, Modularity, Testability).
* **Explicit Module Boundaries:** Clearly define what constitutes a module's public API versus its internal implementation details.
* **Practical Code Size Limits:** Set reasonable guidelines for file length and function complexity to keep the code easy to understand and refactor.
* **Documentation Standards:** Outline the requirements for code comments, READMEs, and API documentation.

#### ❌ Do NOT Include:
* **Business Logic or Feature Requirements:** This content belongs in the Product Specification (PS).
* **Technology Choices:** Decisions on frameworks, databases, or libraries belong in the Technology Specification (TS).
* **Abstract Architectural Diagrams:** High-level system design belongs in the Architecture Specification (AS). This document defines the concrete file structure that *implements* the architecture.
* **Overly Rigid or Complex Rules:** The guidelines should be practical and easy to follow. Don't create rules that add friction without providing significant value.
* **Personal Style Preferences:** All conventions should be agreed upon by the team to serve the collective goal of consistency.

### ✍️ Guiding Principles for Your Choices

The "why" behind your structural rules is as important as the rules themselves.

* **Convention Over Configuration:** Whenever possible, adopt the standard conventions established by your language, framework, or community (e.g., standard project layouts for Go or Rust, Rails conventions). This makes it easier for new developers to join the project.
* **Optimize for Readability and Searchability:** The primary goal is to make code easy to find and understand. A developer should be able to guess where a file is located based on its purpose and what a variable does based on its name.
* **Structure Should Reflect Architecture:** The physical layout of your codebase (folders and modules) should mirror the logical components and boundaries defined in your Architecture Specification. If the architecture defines a "Billing Service," there should be a corresponding `billing/` module in the code.

### ⚙️ Application & Enforcement

A specification is only useful if it's followed.

* **Automate with Tooling:** Enforce naming conventions, import order, and code formatting automatically using linters and formatters (e.g., ESLint, Prettier, Black, `gofmt`). This removes the burden of manual enforcement during code reviews.
* **Make it Part of the Workflow:** Reference this document during onboarding and make adherence a standard part of your team's code review checklist.
* **Document the "Why":** For any non-obvious convention, add a brief note in the spec explaining the rationale. This helps with team buy-in and prevents future debates.