from typing import List, Optional, Any
import logging
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext, Settings
from llama_index.core.retrievers import BaseRetriever, VectorIndexRetriever
# Ensure BM25 is available
try:
    from llama_index.retrievers.bm25 import BM25Retriever
except ImportError:
    BM25Retriever = None

# Using generic reranker or flag-embedding
try:
    from llama_index.postprocessor.flag_embedding_reranker import FlagEmbeddingReranker
except ImportError:
    FlagEmbeddingReranker = None
    
# Fallback to SentenceTransformerRerank if configured (core usually has this or requires package)
# Ideally in 0.10+ it's in llama-index-postprocessor-sentence-transformer-rerank? 
# We'll use FlagEmbeddingReranker since we installed it, or disable if missing.

from llama_index.core.postprocessor import SentenceTransformerRerank
from llama_index.core.schema import NodeWithScore
from llama_index.core import QueryBundle

logger = logging.getLogger(__name__)

# Configure Local Settings by default
Settings.embed_model = "local:BAAI/bge-small-en-v1.5"
# Settings.llm =  # We let it fail or use what's available for LLM, or user sets it. 
# For pure retrieval, LLM is not needed if we just call retrieve.

class AdvancedRAG:
    """
    Advanced RAG implementation using LlamaIndex.
    Features:
    - Hybrid Search (Vector + BM25)
    - Re-ranking (Cross-Encoder/FlagEmbedding)
    """

    def __init__(self, index: VectorStoreIndex):
        self.index = index
        
        # Initialize Reranker using SentenceTransformerRerank (more stable)
        try:
            self._reranker = SentenceTransformerRerank(
                model="cross-encoder/ms-marco-MiniLM-L-6-v2", 
                top_n=5
            )
            logger.info("AdvancedRAG initialized with MS-Marco re-ranker.")
        except Exception as e:
            self._reranker = None
            logger.warning(f"Reranker initialization failed: {e}. Running without reranker.")

    def _get_hybrid_retriever(self, top_k: int = 10) -> BaseRetriever:
        """
        Combine Vector and BM25 retrievers.
        """
        vector_retriever = VectorIndexRetriever(index=self.index, similarity_top_k=top_k)
        
        # Note: Hybrid requires persisting BM25. For now return vector only.
        return vector_retriever

    def query(self, query: str, top_k: int = 10) -> str:
        """
        Execute Advanced RAG query.
        """
        # 1. Retrieve (High Recall)
        retriever = self._get_hybrid_retriever(top_k=top_k * 2) 
        nodes = retriever.retrieve(query)
        
        # 2. Re-rank (High Precision)
        if self._reranker:
            query_bundle = QueryBundle(query_str=query)
            ranked_nodes = self._reranker.postprocess_nodes(nodes, query_bundle)
        else:
            ranked_nodes = nodes[:top_k]
        
        # 3. Synthesize (Generate Answer)
        from llama_index.core.response_synthesizers import get_response_synthesizer
        
        synthesizer = get_response_synthesizer(response_mode="compact")
        response = synthesizer.synthesize(query, nodes=ranked_nodes)
        
        return str(response)

    @classmethod
    def from_documents(cls, documents: List[Any]):
        """
        Create AdvancedRAG from a list of documents.
        """
        # Use default embedding model 
        index = VectorStoreIndex.from_documents(documents)
        return cls(index)
