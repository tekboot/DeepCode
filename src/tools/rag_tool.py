#!/usr/bin/env python
"""
RAG Query Tool - Wrapper for RAG query functionality
Supports both LightRAG (Graph) and AdvancedRAG (LlamaIndex + Re-ranking)
"""

import asyncio
from pathlib import Path
import sys
import logging

# Add parent directory to path (insert at front to prioritize project modules)
project_root = Path(__file__).parent.parent.parent
# Add raganything module path
raganything_path = project_root.parent / "raganything" / "RAG-Anything"
if raganything_path.exists():
    sys.path.insert(0, str(raganything_path))

from dotenv import load_dotenv
from lightrag.llm.openai import openai_complete_if_cache, openai_embed
from lightrag.utils import EmbeddingFunc
from raganything import RAGAnything, RAGAnythingConfig

from src.core.core import get_embedding_config, get_llm_config
from src.core.logging import LightRAGLogContext
from src.knowledge.manager import KnowledgeBaseManager

# Import AdvancedRAG
from src.knowledge.advanced_rag import AdvancedRAG
# Note: In a real app, we'd load the persistent index. For now we mock or build on fly if needed.

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv(project_root / "DeepTutor.env", override=False)
load_dotenv(project_root / ".env", override=False)


async def rag_search(
    query: str,
    kb_name: str | None = None,
    mode: str = "hybrid",
    api_key: str | None = None,
    base_url: str | None = None,
    kb_base_dir: str | None = None,
    **kwargs,
) -> dict:
    """
    Query knowledge base using RAG.
    Supports routing to AdvancedRAG for enhanced retrieval if specified.
    """
    
    # Check if we should use AdvancedRAG (e.g. explicit mode or specific KB type)
    if mode == "advanced":
        try:
            # TODO: Load actual persistent LlamaIndex for this KB
            # For now, this branch is a placeholder for the LlamaIndex integration
            # In production, we would initialize AdvancedRAG(storage_context=...) here.
            
            # Temporary Fallback to normal RAG until Index persistence is implemented
            logger.warning("Advanced RAG mode requested but persistence not fully set up. Falling back to Hybrid LightRAG.")
            mode = "hybrid" 
        except Exception as e:
            logger.error(f"Advanced RAG failed: {e}")
            mode = "hybrid"

    # Get LLM configuration
    try:
        llm_config = get_llm_config()
    except ValueError as e:
        raise ValueError(f"LLM configuration error: {e!s}")

    # Get Embedding configuration
    try:
        embedding_config = get_embedding_config()
    except ValueError as e:
        raise ValueError(f"Embedding configuration error: {e!s}")

    # Override configuration with provided parameters (if provided)
    llm_api_key = api_key or llm_config["api_key"]
    llm_base_url = base_url or llm_config["base_url"]
    llm_model = llm_config["model"]

    embedding_api_key = embedding_config["api_key"]
    embedding_base_url = embedding_config["base_url"]
    embedding_model = embedding_config["model"]
    embedding_dim = embedding_config["dim"]
    embedding_max_tokens = embedding_config["max_tokens"]

    # If knowledge base path not specified, try to get from config
    if kb_base_dir is None:
        try:
            from src.core.core import get_path_from_config, load_config_with_main

            project_root = Path(__file__).parent.parent.parent
            # Try loading from solve_config (most common)
            config = load_config_with_main("solve_config.yaml", project_root)
            kb_base_dir = get_path_from_config(config, "knowledge_bases_dir") or config.get(
                "tools", {}
            ).get("rag_tool", {}).get("kb_base_dir")
            if kb_base_dir:
                kb_base_dir = str(kb_base_dir)
        except Exception:
            pass

        # Fallback to default path
        if kb_base_dir is None:
            project_root = Path(__file__).parent.parent.parent
            kb_base_dir = str(project_root / "data" / "knowledge_bases")

    # Use KnowledgeBaseManager to get RAG storage path
    try:
        kb_manager = KnowledgeBaseManager(kb_base_dir)
        working_dir = str(kb_manager.get_rag_storage_path(kb_name))
    except ValueError as e:
        # If rag_storage doesn't exist, try using traditional path
        if "RAG storage not found" in str(e):
            if kb_name:
                kb_dir = Path(kb_base_dir) / kb_name
            else:
                kb_dir = Path(kb_base_dir) / kb_manager.get_default()
            working_dir = str(kb_dir / "rag_storage")
            # If still doesn't exist, provide friendly message
            if not Path(working_dir).exists():
                raise ValueError(
                    "Error: Knowledge base RAG storage not initialized\nHint: Please run init_knowledge_base.py to initialize the knowledge base"
                )
        else:
            raise ValueError(f"Error: {e!s}")
    except Exception as e:
        raise Exception(f"Error: Unable to access knowledge base - {e!s}")

    # Define LLM function
    def llm_model_func(prompt, system_prompt=None, history_messages=[], **kwargs):
        return openai_complete_if_cache(
            llm_model,
            prompt,
            system_prompt=system_prompt,
            history_messages=history_messages,
            api_key=llm_api_key,
            base_url=llm_base_url,
            **kwargs,
        )

    # Define embedding function
    embedding_func = EmbeddingFunc(
        embedding_dim=embedding_dim,
        max_token_size=embedding_max_tokens,
        func=lambda texts: openai_embed(
            texts,
            model=embedding_model,
            api_key=embedding_api_key,
            base_url=embedding_base_url,
        ),
    )

    # Create RAG instance (LightRAG)
    config = RAGAnythingConfig(
        working_dir=working_dir,
        enable_image_processing=True,
        enable_table_processing=True,
        enable_equation_processing=True,
    )

    # Use log forwarding context manager
    with LightRAGLogContext(scene="rag_tool"):
        rag = RAGAnything(
            config=config,
            llm_model_func=llm_model_func,
            embedding_func=embedding_func,
        )

        # Ensure initialization
        await rag._ensure_lightrag_initialized()

        # Execute query
        try:
            answer = await rag.aquery(query, mode=mode, **kwargs)
            answer_str = answer if isinstance(answer, str) else str(answer)

            return {"query": query, "answer": answer_str, "mode": mode}
        except Exception as e:
            raise Exception(f"Query failed: {e!s}")


if __name__ == "__main__":
    import sys

    if sys.platform == "win32":
        import io

        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

    # Test
    result = asyncio.run(
        rag_search(
            "What is the lookup table (LUT) in FPGA?",
            kb_name="DE-all",
            mode="naive",
            only_need_context=False,
        )
    )

    print(f"Query: {result['query']}")
    print(f"Answer: {result['answer']}")
