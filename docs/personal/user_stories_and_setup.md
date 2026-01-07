# DeepTutor: User Stories & Comprehensive Setup Guide

This document outlines the capabilities of DeepTutor (User Stories) and provides a complete guide to configuring and running the system locally, including all Phase 5 (Multi-Source) extensions.

---

## 1. User Stories

### 🧑‍💻 As a Software Developer
*   **Contextual Code Search**: "I want to find where `AuthService` validates tokens, even if I don't know the exact file name."
    *   *Enabled by:* Phase 2 (Advanced RAG Retrieval).
*   **Architecture Understanding**: "I want to understand *why* we used a Factory pattern in `src/ingestion`, citing the design docs."
    *   *Enabled by:* Phase 3 (Socratic Mentor) & Phase 5 (Confluence Connector).
*   **Debugging Assistant**: "I want to paste an error stack trace and have DeepTutor find the relevant code and Jira tickets related to similar past bugs."
    *   *Enabled by:* Phase 2 (Hybrid Search) & Phase 5 (Jira Connector).

### 👩‍✈️ As a Tech Lead / Architect
*   **Design Verification**: "I want to verify if the implementation of `GitHubConnector` matches the specs defined in Confluence."
    *   *Enabled by:* Phase 5 (Multi-Source Ingestion).
*   **Onboarding**: "I want new hires to ask 'How do I run the project on Windows?' and get a step-by-step guide from our internal READMEs."
    *   *Enabled by:* Phase 1 (Ingestion) & Phase 3 (Mentor).
*   **Privacy Compliance**: "I want to ensure no PII (emails, names) from our production logs enters the knowledge base."
    *   *Enabled by:* Phase 1 (Privacy Guard).

### 🕵️ As a Product Owner
*   **Requirement Tracing**: "I want to link a Jira Feature Request to the specific Pull Request that implemented it."
    *   *Enabled by:* Phase 5 (Jira & GitHub Connectors).
*   **Status Updates**: "I want to ask 'What is the status of the 'Multi-Source' feature?' and get a summary based on recent Slack updates and Jira tickets."
    *   *Enabled by:* Phase 5 (Slack & Jira Connectors).

---

## 2. Comprehensive Setup Guide

### prerequisites
1.  **Python 3.10+** (Recommend 3.12).
2.  **Git**.
3.  **Visual Studio Build Tools** (C++ Desktop Development workload) - Required for Windows.

### Installation
1.  **Clone & Enter**:
    ```powershell
    git clone https://github.com/your-org/DeepTutor.git
    cd DeepTutor
    ```
2.  **Virtual Environment**:
    ```powershell
    python -m venv venv
    .\venv\Scripts\Activate.ps1
    ```
3.  **Install Dependencies**:
    ```powershell
    pip install -r requirements.txt
    ```
4.  **Download Privacy Models**:
    ```powershell
    python -m spacy download en_core_web_sm
    ```

---

## 3. Configuration (Environment Variables)

Create a `.env` file in the root directory. Add the keys corresponding to the connectors you wish to use.

### Core (Optional for Local Mode)
```env
OPENAI_API_KEY=sk-...  # Only if using OpenAI models instead of Local
```

### GitHub Connector
```env
GITHUB_TOKEN=ghp_...   # Personal Access Token (Repo scope)
```

### Jira Connector (Phase 5)
```env
JIRA_EMAIL=your_email@company.com
JIRA_API_TOKEN=ATATT...  # Atlassian API Token
JIRA_SERVER_URL=https://your-domain.atlassian.net
```

### Confluence Connector (Phase 5)
```env
CONFLUENCE_USERNAME=your_email@company.com
CONFLUENCE_API_TOKEN=ATATT... # Same as Jira Token usually
CONFLUENCE_URL=https://your-domain.atlassian.net/wiki
```

### Slack Connector (Phase 5)
```env
SLACK_BOT_TOKEN=xoxb-... # Bot User OAuth Token
```

---

## 4. Running the Project

### A. Verification Scripts
Run these to ensure your environment is correctly set up.

1.  **Verify Core & Connectors (Privacy, GitHub, Jira, Slack, Confluence)**:
    ```powershell
    python src/ingestion/verify_setup.py
    ```
    *Expectation*: "✅ [Connector] registered and retrieved successfully" for all defined connectors.

2.  **Verify Advanced RAG (Retrieval & Re-ranking)**:
    ```powershell
    python src/knowledge/verify_advanced_rag.py
    ```
    *Expectation*: Successful retrieval and re-ranking of sample queries.

### B. Evaluation Benchmark
Run the baseline evaluation against the Golden Set to measure performance.
```powershell
python src/evaluation/run_eval.py
```

### C. Future: Web UI (Phase 6)
*Coming Soon: `python src/server/app.py`*
