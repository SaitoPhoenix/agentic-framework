## Guidelines for Writing a Technology Specification (TS)

A Technology Specification (TS) is the bridge between abstract architecture and concrete implementation. It serves as the definitive guide to the tools, libraries, and processes used to build the software.

### The Golden Rule: Be Specific and Justify Everything
The purpose of this document is to eliminate ambiguity. While the Architecture Spec focuses on the "what" and the Product Spec on the "why," the Technology Spec details the **"how"** and provides the **rationale** for those choices. Every major decision recorded here should be backed by a clear justification.

### Content & Structure Checklist

Your Technology Specification should be a comprehensive reference for the entire engineering team. Ensure it captures the following information.

#### ✅ Do Include:
* **A Definitive Technology List:** Specify the exact languages, frameworks, and platforms that will be used.
* **Specific Version Numbers:** Whenever possible, state the major version (e.g., `Python 3.11+`, `PostgreSQL 15.x`) to ensure environment consistency.
* **Clear Justifications:** For every major technology choice, explain *why* it was selected. Reference performance needs, team expertise, ecosystem maturity, or specific product requirements.
* **Key Dependencies:** List critical third-party libraries and external services (e.g., payment gateways, auth providers).
* **Concrete Data Schemas:** Include detailed diagrams like Entity-Relationship Diagrams (ERDs) that define the structure of your data.
* **Development & CI/CD Processes:** Document the tools and workflows for building, testing, and deploying the software, including the version control strategy.
* **A Decision Log:** Keep a running list of key technical decisions, the alternatives considered, and the final rationale.
* **Known Limitations & Tech Debt:** Be transparent about trade-offs, shortcuts taken, and areas that will need future improvement.

#### ❌ Do NOT Include:
* **Product Requirements or User Stories:** This content belongs in the Product Specification (PS).
* **High-Level, Abstract Architectural Diagrams:** Those belong in the Architecture Specification (AS). Diagrams in the TS should be concrete and detailed (e.g., ERDs, network diagrams).
* **Vague Justifications:** Avoid weak reasons like "it's popular" or "it's cool." Justifications must be tied to a tangible benefit for the project.
* **Marketing or User-Facing Content:** This is a technical document for internal teams.
* **Project Management Details:** Timelines, sprint plans, and team assignments belong in project management tools.

### ✍️ Rationale & Justification Guidelines

The quality of your justifications is what makes this document truly valuable.

* **Reference Other Specs:** Connect your choices back to the foundational documents.
    * **Example:** "We selected **Neo4j** (TS) to implement the **'Knowledge Graph'** component (AS) needed to support the **'Anonymous Mentor Matching'** feature (PS)."
* **Acknowledge Trade-offs:** No decision is perfect. A strong justification explains the benefits of the chosen technology and also acknowledges the downsides or alternatives that were rejected.
    * **Example:** "We chose an external API for AI services to accelerate our MVP timeline, accepting the trade-off of higher long-term costs and less control compared to a self-hosted model."
* **Be Precise and Data-Driven:** Whenever possible, base decisions on objective criteria. This could be performance benchmarks, security compliance, licensing costs, or the availability of skilled developers.

### 📊 Diagramming & Schema Standards

Visuals in a Technology Specification should provide concrete clarity, not abstract overviews.

* **Focus on Implementation Details:** Diagrams should illustrate the specific structure of a system. ERDs for database schemas are a perfect example. Other useful diagrams could include sequence diagrams for API calls or network topology diagrams.
* **Use Standard, Reproducible Formats:** Use tools like Mermaid, PlantUML, or database design tools that allow diagrams to be stored as code and version-controlled alongside the specification.
* **Keep Diagrams Focused:** Each diagram should have a clear purpose and illustrate a specific part of the system. Avoid creating a single, monolithic diagram that tries to show everything.