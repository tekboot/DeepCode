import sys
import os
import logging
from llama_index.core import Document

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DeepTutor-Verifier")

def verify_advanced_rag():
    logger.info("Verifying AdvancedRAG...")
    try:
        from src.knowledge.advanced_rag import AdvancedRAG
        
        # Create dummy documents
        docs = [
            Document(text="DeepTutor is an AI tutoring system developed by HKU Data Intelligence Lab."),
            Document(text="Python is a popular programming language for AI."),
            Document(text="LlamaIndex is a data framework for LLMs."),
            Document(text="Watermelons are delicious fruits."),
        ]
        
        # Initialize AdvancedRAG (indexes documents in memory)
        logger.info("Initializing AdvancedRAG with dummy documents...")
        rag = AdvancedRAG.from_documents(docs)
        
        # Query
        query = "Who developed DeepTutor?"
        logger.info(f"Querying: {query}")

        # 1. Test Retrieval (No LLM needed)
        logger.info("Testing retrieval...")
        retriever = rag._get_hybrid_retriever(top_k=2)
        nodes = retriever.retrieve(query)
        logger.info(f"Retrieved {len(nodes)} nodes.")
        for node in nodes:
            logger.info(f" - {node.text[:50]}...")
            
        if any("HKU" in n.text for n in nodes):
             logger.info("✅ Retrieval verification successful.")
        else:
             logger.error("❌ Retrieval verification failed.")
             
        # 2. Test Reranking (No LLM needed)
        logger.info("Testing Reranking...")
        if rag._reranker:
            from llama_index.core import QueryBundle
            ranked = rag._reranker.postprocess_nodes(nodes, QueryBundle(query))
            logger.info(f"Reranked {len(ranked)} nodes.")
            if len(ranked) > 0:
                logger.info("✅ Reranking verification successful.")
        else:
            logger.warning("Reranker skipped (not initialized).")

        # 3. Test Synthesis (Optional - requires LLM)
        # try:
        #     response = rag.query(query)
        #     logger.info(f"Response: {response}")
        # except Exception as e:
        #     logger.warning(f"Synthesis failed (likely no LLM): {e}")
            
    except Exception as e:
        logger.error(f"❌ AdvancedRAG verification failed: {e}")

if __name__ == "__main__":
    verify_advanced_rag()
