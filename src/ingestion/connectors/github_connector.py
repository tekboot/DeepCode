from typing import List, Dict, Any, Optional
import os
import logging
from .base import BaseConnector, DeepTutorDocument, ConnectorFactory

logger = logging.getLogger(__name__)

class GitHubConnector(BaseConnector):
    """
    Connector for GitHub Repositories using LlamaIndex.
    """
    
    def load_data(self, config: Dict[str, Any]) -> List[DeepTutorDocument]:
        """
        Load data from a GitHub repository.
        Config requires:
        - github_token: Personal Access Token
        - owner: Repository owner
        - repo: Repository name
        - branch: (Optional) Branch to load, defaults to 'main'
        """
        try:
            from llama_index.readers.github import GithubRepositoryReader, GithubClient
        except ImportError:
            raise ImportError("llama-index-readers-github is not installed. Please install it.")

        github_token = config.get("github_token")
        owner = config.get("owner")
        repo = config.get("repo")
        branch = config.get("branch", "main")
        
        if not github_token or not owner or not repo:
            raise ValueError("Missing required config: github_token, owner, repo")

        logger.info(f"Loading GitHub Repo: {owner}/{repo} (branch: {branch})")

        github_client = GithubClient(github_token=github_token)
        loader = GithubRepositoryReader(
            github_client=github_client,
            owner=owner,
            repo=repo,
            filter_file_extensions=[".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".json", ".ipynb"],
            verbose=False,
            concurrent_requests=5
        )

        llama_docs = loader.load_data(branch=branch)
        
        deep_tutor_docs = []
        for doc in llama_docs:
            # Normalize to DeepTutorDocument
            dt_doc = DeepTutorDocument(
                content=doc.text,
                source_type="github",
                source_id=doc.metadata.get("file_path") or doc.metadata.get("url") or "unknown",
                metadata=doc.metadata,
                privacy_level="private" # Default to private for ingested repos
            )
            deep_tutor_docs.append(dt_doc)
            
        logger.info(f"Successfully loaded {len(deep_tutor_docs)} documents from GitHub.")
        return deep_tutor_docs

# Register the connector
ConnectorFactory.register("github", GitHubConnector)
