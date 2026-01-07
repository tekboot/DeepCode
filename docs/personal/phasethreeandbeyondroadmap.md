# DeepTutor Roadmap: Phase 3 & Beyond

## Phase 3: The Interactive Mentor (Current Focus)
**Goal**: Transform DeepTutor from a passive retrieval system into an active, Socratic guide that helps developers "learn" rather than just "copy-paste".

### 1. Socratic Persona Implementation
*   **Objective**: Update agent system prompts to restrict direct answer generation when "learning" mode is active.
*   **Tasks**:
    *   Update `src/agents/solve/prompts/en/solve_loop/solve_agent.yaml` to include "Pedagogical Strategy".
    *   Update `response_agent.yaml` to frame answers as guided derivations.
    *   Implement "Concept Check" questions (Agent asks user "Do you understand why we use X here?" before proceeding).

### 2. Citational & Grounded Logic
*   **Objective**: Zero Hallucination Policy.
*   **Tasks**:
    *   Enforce `[Source-ID]` citation format in `response_agent.yaml`.
    *   Implement a post-processing validator that flags answers without citations.
    *   Modify `AdvancedRAG` to return precise source metadata (line numbers, file paths) for the UI to render clickable links.

### 3. Visual Explanation (IdeaGen Integration)
*   **Objective**: Explain code through diagrams.
*   **Tasks**:
    *   Integrate existing `InteractiveAgent` capabilities into the main loop.
    *   Trigger Mermaid diagram generation for queries involving "Architecture", "Flow", "Class Hierarchy".

---

## Phase 4: Evaluation & Refinement
**Goal**: Quantify performance and ensure stability before general release.

### 1. Evaluation Dataset (Golden Set)
*   **Objective**: Create a ground-truth dataset for regression testing.
*   **Tasks**:
    *   Generate 50+ Q&A pairs across: Knowledge Retrieval, Code Debugging, and System Architecture.
    *   Include "Adversarial Examples" (questions not in the docs) to test refusal capabilities.

### 2. Automated Metrics (RAGAS / Trulens)
*   **Objective**: Measure RAG quality.
*   **Tasks**:
    *   **Faithfulness**: Does the answer hallucinate?
    *   **Answer Relevance**: Does it address the query?
    *   **Context Precision**: Did retrieval find the right chunks?

### 3. UI Integration & Polish
*   **Objective**: Seamless User Experience.
*   **Tasks**:
    *   Connect the Python backend to the Frontend (Next.js/React).
    *   Render "Thought Chains" (show user *how* the agent is thinking).
    *   Render Mermaid diagrams dynamically.

---

## Phase 5: Future Expansion (Long-Term)

### 1. Additional Connectors
*   **Jira & Slack**: Integrate communication channels to answer "Why was this decision made?"
*   **Confluence**: Ingest high-level design docs.
*   **Google Drive/Gmail**: Project specs and requirement emails.

### 2. Multimodal Ingestion
*   **Architecture Diagrams**: Use VLMs (Vision Language Models) to ingest `.png`/`.jpg` architecture diagrams and convert them to text descriptions for indexing.
*   **Video Summaries**: Process meeting recordings (transcripts) related to code.

### 3. Personalized Learning Paths
*   **User Modeling**: Track user's knowledge state (what concepts they have mastered).
*   **Curriculum Generation**: Suggest next topics based on the codebase (e.g., "You've mastered the API layer, now learn the Database Schema").
