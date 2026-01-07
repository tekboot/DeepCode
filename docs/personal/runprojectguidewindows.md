# DeepTutor: Local Run Guide (Windows)

This document provides step-by-step instructions to set up and run the current iteration of DeepTutor (Phase 1 & Phase 2) on a Windows machine.

## Prerequisites
Ensure you have the following installed on your system:
1.  **Python 3.10 or higher** (Python 3.12 recommended).
    *   Verify with: `python --version`
2.  **Git** (for cloning the repository).
    *   Verify with: `git --version`
3.  **Visual Studio Build Tools** (Required for compiling some Python packages like `ujson` or `sentence-transformers` on Windows).
    *   Install "Desktop development with C++" workload if you encounter "Microsoft Visual C++ 14.0 or greater is required" errors.

---

## 1. Setup Environment

### Clone the Repository
```powershell
git clone <repository-url>
cd DeepTutor
```

### Create Virtual Environment
It is highly recommended to use a virtual environment to manage dependencies.
```powershell
# Create venv
python -m venv venv

# Activate venv
.\venv\Scripts\Activate.ps1
```
*(If you get a PSSecurityException, run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`)*

### Install Dependencies
Install all required Python packages. This includes LlamaIndex, Presidio, Torch, and others.
```powershell
pip install -r requirements.txt
```
*Note: This step may take several minutes as it downloads PyTorch and NVIDIA CUDA libraries if available.*

### Download SpaCy Model
Required for privacy scrubbing (Presidio).
```powershell
python -m spacy download en_core_web_sm
```

---

## 2. Configuration

### Environment Variables
1.  Create a copy of `.env.example` (if exists) or create a new `.env` file in the root directory.
2.  Add the following keys (if you plan to use external LLMs, though the current Verification scripts run locally):
```env
# Optional for Phase 1 & 2 Verification (Local Mode)
OPENAI_API_KEY=sk-... 
GITHUB_TOKEN=ghp_... (For GitHub Connector testing)
```

---

## 3. Running Verifications

### Phase 1: Verify Privacy Guard & Connectors
Tests PII scrubbing and Connector Factory registration.
```powershell
python src/ingestion/verify_setup.py
```
**Expected Output:**
*   Logs showing "PrivacyGuard initialized..."
*   Example text with PII replaced by `<PERSON>`, `<EMAIL>`.
*   "GitHubConnector registered successfully."

### Phase 2: Verify Advanced RAG (Retrieval)
Tests the LlamaIndex integration, Hybrid Search logic, and Re-ranking.
```powershell
python src/knowledge/verify_advanced_rag.py
```
**Expected Output:**
*   Initialization of `AdvancedRAG` with `MS-Marco-MiniLM` re-ranker.
*   "Testing retrieval..." -> Shows retrieved document nodes.
*   "Testing Reranking..." -> Shows re-ranked nodes.
*   "✅ Retrieval verification successful."

---

## 4. Troubleshooting Common Windows Issues

*   **Long Paths**: Windows has a MAX_PATH limit of 260 characters. If you see "File not found" errors during install, enable Long Paths in Registry Editor or move the project to a shorter path (e.g., `C:\Dev\DeepTutor`).
*   **Encoding Errors**: If you see `UnicodeDecodeError` in the console, set the Python encoding environment variable:
    ```powershell
    $env:PYTHONUTF8=1
    ```
*   **Missing C++ Tools**: Ensure Visual Studio Build Tools are installed if `pip install` fails on compilation steps.
