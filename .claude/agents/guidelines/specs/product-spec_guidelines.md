## Guidelines for Writing a Product Specification (PS)

A Product Specification (PS) is the foundational document for any project. It serves as the single source of truth for the product's vision, goals, and requirements.

### The Golden Rule: Focus on the Problem, Not the Implementation
Your primary goal is to define the **problem** you are solving, the **users** you are solving it for, and the **value** you will deliver. Avoid prescribing the technical solution. The PS answers the "why" and "what," leaving the "how" to the architecture and design specifications.

### Content & Structure Checklist

A strong Product Spec should be comprehensive but not overly prescriptive about its structure. Ensure the following concepts are clearly articulated in your document.

#### ✅ Do Include:
* **The Core Vision:** Clearly state the project's "North Star." This includes the high-level purpose and the problem you're solving.
* **Target User Definition:** Define who the product is for. This often takes the form of personas, including their goals and primary pain points.
* **User Problems & Requirements:** Translate user needs into specific requirements. User stories ("As a..., I want to..., so that...") are an excellent format for this.
* **Measurable Business Goals:** Define what success looks like for the business. Every goal should be tied to a specific, measurable metric (KPI).
* **Clear Scope Boundaries:** Explicitly list what is **in scope** and **out of scope** for the release. This is critical for managing expectations and preventing scope creep.
* **High-Level Feature Breakdown:** Group the required features into logical themes (often called Epics). Describe what the system needs to do from a user's perspective.
* **Forward-Looking Context:** Briefly mention potential ideas for future versions to show long-term vision without committing to them in the current scope.

#### ❌ Do NOT Include:
* **Technical Implementation Details:** Avoid mentioning specific databases, programming languages, APIs, or architectural patterns.
* **Detailed UI/UX Designs:** High-fidelity mockups or pixel-perfect designs belong in a design specification. Low-fidelity wireframes are acceptable if they help clarify a requirement.
* **Engineering Timelines or Task Breakdowns:** Sprint plans, resource allocation, and specific engineering tasks belong in project management tools.
* **Vague or Unmeasurable Goals:** Avoid subjective goals like "make a better user experience." Instead, use measurable metrics like "reduce the number of clicks to complete task X by 50%."

### ✍️ Language & Terminology Guidelines

* **Stay User-Centric:** Frame every feature and requirement in terms of the value it provides to the user. Always tie the "what" back to the "who" and "why."
* **Be Clear and Unambiguous:** Use simple, direct language. This document must be easily understood by a diverse audience, from business stakeholders to junior engineers. Avoid internal jargon.
* **Focus on Outcomes, Not Output:** Describe the desired result, not the specific feature to be built.
    * **Instead of:** "Build a dashboard with three charts."
    * **Write:** "Provide managers with a way to visualize their team's key performance metrics at a glance."

### 🎨 Visuals & Diagrams

While a PS is primarily text-based, visuals can significantly improve clarity.

* **Use Low-Fidelity Visuals:** If you include diagrams, they should be simple and conceptual. User flow diagrams, basic wireframes, or concept maps are appropriate.
* **Clarify, Don't Design:** The goal of a visual in a PS is to clarify a complex requirement or user journey, not to define the final look and feel of the interface.