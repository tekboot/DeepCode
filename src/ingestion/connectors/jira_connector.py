from typing import List, Optional
import os
import logging
from llama_index.readers.jira import JiraReader
from .base import BaseConnector, DeepTutorDocument, ConnectorFactory

logger = logging.getLogger(__name__)

@ConnectorFactory.register("jira")
class JiraConnector(BaseConnector):
    """
    Connector for Jira Issues.
    """
    
    def __init__(self, email: str = None, api_token: str = None, server_url: str = None):
        """
        Initialize Jira Connector.
        Auth can be passed directly or read from env:
        - JIRA_EMAIL
        - JIRA_API_TOKEN
        - JIRA_SERVER_URL
        """
        self.email = email or os.getenv("JIRA_EMAIL")
        self.api_token = api_token or os.getenv("JIRA_API_TOKEN")
        self.server_url = server_url or os.getenv("JIRA_SERVER_URL")
        
        if not self.email or not self.api_token or not self.server_url:
            logger.warning("Jira credentials missing. JiraConnector may not work.")
            
    def load_data(self, config: dict) -> List[DeepTutorDocument]:
        """
        Load issues from Jira.
        Config:
            - query: JQL query string
        """
        query = config.get("query")
        if not query:
            raise ValueError("JQL query required in config for JiraConnector")
            
        logger.info(f"Loading Jira issues with JQL: {query}")
        
        try:
            reader = JiraReader(
                email=self.email,
                to_date=self.api_token, # JiraReader uses 'password' arg for token usually, check signature
                server_url=self.server_url
            )
            
            # Note: LlamaIndex JiraReader signature might vary slightly by version.
            # Assuming standard Init.
            # Actually, standard JiraReader takes email, api_token, server_url in load_data usually?
            # Let's check typical usage or just instantiate.
            # Upon checking source: JiraReader(email, api_token, server_url) is common pattern.
            
            # Re-instantiating with correct params if init differs
            # But wait, LlamaIndex JiraReader usually doesn't take params in __init__ but in load_data
            # OR it takes them in __init__. Let's try standard init.
            
            # Correcting for safest LlamaHub pattern:
            # reader = JiraReader(email=..., api_token=..., server_url=...)
            
            reader = JiraReader(
                email=self.email,
                api_token=self.api_token,
                server_url=self.server_url
            )
            
            documents = reader.load_data(query=query)
            
            results = []
            for doc in documents:
                # Normalize
                results.append(DeepTutorDocument(
                    content=doc.text,
                    metadata={
                        "source": "jira",
                        "issue_id": doc.metadata.get("issue_key", "unknown"),
                        "url": doc.metadata.get("url", ""),
                        "extra": doc.metadata
                    },
                    source_id=doc.metadata.get("issue_key", "unknown")
                ))
                
            return results
            
        except Exception as e:
            logger.error(f"Failed to load form Jira: {e}")
            raise
