# DeepTutor Phase 1 & 2 Implementation Documentation

## Overview
This document details the architectural changes and implementations completed during Phase 1 (Foundation) and Phase 2 (Advanced RAG) of the DeepTutor expansion project. The goal was to establish a secure, multi-source ingestion pipeline and an advanced retrieval system capable of deep contextual understanding.

## Phase 1: Foundation (Privacy & Connectors)

### 1. Privacy Guard (`scrub-then-ingest`)
To adhere to the "Local-First" and "Privacy-Centric" design philosophy, we implemented a robust PII scrubbing layer that processes all data *before* it enters the knowledge base.

*   **Component**: `src.ingestion.privacy_guard.PrivacyGuard`
*   **Technology**: Microsoft Presidio (Local Analysis & Anonymization)
*   **Model**: `en_core_web_sm` (SpaCy)
*   **Functionality**:
    *   **Analyze**: Detects PII entities such as Names, Emails, Phone Numbers, and IP Addresses.
    *   **Anonymize**: Replaces detected entities with placeholders (e.g., `<PERSON>`, `<EMAIL>`).
    *   **Safety Check**: Provides a boolean check to ensure content is safe for storage.

### 2. Connector Architecture
We established a unified connector pattern to support diverse data sources (GitHub, Jira, Confluence, etc.) while ensuring normalized output.

*   **Base Classes**: `src.ingestion.connectors.base.BaseConnector` & `ConnectorFactory`
*   **Data Model**: `DeepTutorDocument`
    *   Unified dataclass schema containing content, metadata, source type, related IDs (links), and privacy level.
*   **GitHub Connector**: `src.ingestion.connectors.github_connector.GitHubConnector`
    *   Wraps `LlamaIndex`'s `GithubRepositoryReader`.
    *   Authenticates via Personal Access Token (PAT).
    *   Automatically converts repository files into normalized `DeepTutorDocument` objects.

### 3. Verification
*   **Script**: `src/ingestion/verify_setup.py`
    *   Validates PII scrubbing on sample text.
    *   Confirms Connector Factory registration and GitHub connection.

---

## Phase 2: Advanced RAG (Indexing & Retrieval)

### 1. Advanced RAG Module
We upgraded the retrieval system to go beyond simple vector search, enabling "Hybrid Search" and "Re-ranking" for higher precision.

*   **Component**: `src.knowledge.advanced_rag.AdvancedRAG`
*   **Technology**: LlamaIndex Framework
*   **Embeddings**: Local BAAI/bge-small-en-v1.5 (No external API dependency for embeddings).
*   **Key Features**:
    *   **Hybrid Search**: Although currently relying on Vector search, the architecture is designed to merge Sparse (BM25) and Dense (Vector) results.
    *   **Re-ranking**: Implemented using `SentenceTransformerRerank` (Cross-Encoder).
    *   **Model**: `cross-encoder/ms-marco-MiniLM-L-6-v2`. This model takes the top-K retrieved candidates and re-scores them based on true relevance to the query, significantly reducing hallucinations.

### 2. DeepTutor Rag Tool Integration
*   **File**: `src/tools/rag_tool.py`
*   **Update**: Modified to dispatch queries to `AdvancedRAG` logic when `mode="advanced"` is requested, paving the way for switching between standard `LightRAG` (Graph-based) and `AdvancedRAG` (Re-ranker based) strategies.

### 3. Verification
*   **Script**: `src/knowledge/verify_advanced_rag.py`
    *   Creates an in-memory index of sample documents.
    *   Performs Retrieval (finding relevant nodes).
    *   Performs Re-ranking (confirming the Cross-Encoder correctly identifies the best match).
    *   Confirms zero-egress capability (works without OpenAI API for embeddings).

## Summary of Capabilities
| Feature | Status | Description |
| :--- | :--- | :--- |
| **PII Scrubbing** | ✅ Live | All text can be anonymized locally before storage. |
| **Source Ingestion**| ✅ Live (GitHub) | Scalable factory pattern established. |
| **Retrieval** | ✅ Advanced | Hybrid-ready + Cross-Encoder Re-ranking active. |
| **Data Privacy** | ✅ High | Local Embeddings + Local Presidio Analysis. |
