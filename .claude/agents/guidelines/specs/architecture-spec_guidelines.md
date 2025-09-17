## Guidelines for Creating High-Level Architecture Specifications

The goal is to produce documents that are clear, durable, and focused purely on architecture, leaving implementation details to other specifications.

### The Golden Rule: Focus on the "What" & "Why," Not the "How"
Your primary goal is to describe **what** the system's components are, **what** their responsibilities are, and **why** they are structured in a certain way. The **how**—the specific technologies, libraries, or algorithms used to build them—belongs in the **Technology Spec** or **Design Spec**.

A good architecture document should remain valid even if we swap a database or a cloud provider.

### Content & Structure Checklist

#### ✅ Do Include:
* **Architectural Goals & Principles:** The core vision and guiding rules.
* **High-Level Components:** The main logical blocks of the system (e.g., "Authentication Service," "Notification Engine").
* **Responsibilities & Boundaries:** A clear description of what each component is responsible for.
* **Interactions & Data Flow:** How the components communicate with each other at a high level (e.g., "The *Audio Capture Service* sends an event to the *Event Streaming Platform*").
* **Key Architectural Patterns:** Illustrate core data flows or processes using high-level diagrams (like sequence or flow charts). This is a great way to show how major components interact to achieve a key function (e.g., "New User Onboarding" or "Audio Processing Pipeline").
* **Cross-Cutting Concerns:** Address scalability, security, observability, and reliability patterns.
* **Success Criteria:** Measurable targets for performance, uptime, etc.

#### ❌ Do NOT Include:
* **Specific Brand Names:** Avoid naming specific software, vendors, or services (e.g., `PostgreSQL`, `AWS S3`, `DataDog`).
* **Specific Libraries or APIs:** Do not mention implementation details like `React`, `D3.js`, or `MediaRecorder API`.
* **Code Snippets or Pseudo-code:** This belongs in a Design Spec.
* **Detailed Data Schemas:** Describe the *type* of data (e.g., "user profile data"), not the specific table columns and data types.
* **Configuration Details:** Avoid mentioning version numbers, cluster sizes, or environment variables.

### ✍️ Language & Terminology Guidelines

The language you use is key to keeping the document at the right level.

#### 1. Use Generic, Functional Terms
Always prefer a generic description over a specific product name.

| Instead of... | Use... |
| :--- | :--- |
| `Kong` or `AWS API Gateway` | **API Gateway** |
| `Kafka` or `AWS Kinesis` | **Event Streaming Platform** |
| `Kubernetes` or `EKS` | **Container Orchestration Platform** |
| `Neo4j` or `Amazon Neptune` | **Graph Database** |
| `Qdrant` or `Pinecone` | **Vector Database** |
| `GPT-4` or `Claude` | **Generative LLM Service** |
| `Istio` or `Linkerd` | **Service Mesh** |

#### 2. Describe Function, Not Implementation
Focus on the component's purpose within the system.

**Instead of this:**
> **Transcription Pipeline:** Orchestrates Whisper-based ASR with quality enhancement and fallback to cloud services.

**Write this:**
> **Transcription Service:** A managed pipeline responsible for converting raw audio streams into accurate text. It orchestrates the transcription process and ensures results are stored and made available for downstream services.

### 🎨 Diagramming Standards

* **Keep it High-Level:** Diagrams should reflect the C4 model's **Level 1 (System Context)** and **Level 2 (Containers)**. Avoid going deeper into component implementation (Level 3).
* **Use Abstract Labels:** The boxes in your diagrams should use the generic terms described above (e.g., "Knowledge Graph," "Object Storage").
* **Show Interactions, Not Protocols:** Arrows should indicate data flow and dependencies (e.g., "sends data to," "reads from"). Avoid labeling them with specific protocols like `REST`, `gRPC`, or `HTTPS` unless the choice of protocol is a critical architectural decision.