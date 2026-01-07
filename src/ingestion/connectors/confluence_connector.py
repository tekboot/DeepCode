from typing import List, Optional
import os
import logging
from llama_index.readers.confluence import ConfluenceReader
from .base import BaseConnector, DeepTutorDocument, ConnectorFactory

logger = logging.getLogger(__name__)

@ConnectorFactory.register("confluence")
class ConfluenceConnector(BaseConnector):
    """
    Connector for Confluence Pages.
    """
    
    def __init__(self, url: str = None, api_key: str = None, user_email: str = None):
        """
        Initialize Confluence Connector.
        """
        self.url = url or os.getenv("CONFLUENCE_URL")
        self.api_key = api_key or os.getenv("CONFLUENCE_API_TOKEN") # Atlassian uses API Token as password
        self.user_email = user_email or os.getenv("CONFLUENCE_USERNAME") # Email/Username
        
    def load_data(self, config: dict) -> List[DeepTutorDocument]:
        """
        Load pages from Confluence.
        Config:
            - page_ids: List of specific page IDs
            - cql: Confluence Query Language string
        """
        page_ids = config.get("page_ids")
        cql = config.get("cql")

        if not page_ids and not cql:
            # Default to something? No, risky.
            raise ValueError("page_ids or cql required in config for ConfluenceConnector")
            
        logger.info(f"Loading Confluence pages. IDs: {page_ids}, CQL: {cql}")
        
        try:
            # LlamaIndex ConfluenceReader uses 'base_url', 'oauth2' (dict) or 'user_name'/'api_key'
            # Check latest sig: ConfluenceReader(base_url=None, user_name=None, password=None, cloud=True, api_token=None)
            # It seems 'password' or 'api_token' can be used.
            
            reader = ConfluenceReader(
                base_url=self.url,
                user_name=self.user_email,
                password=self.api_key, # Usually API token goes here for Cloud
                cloud=True
            )
            
            # Load data
            # load_data(page_ids=None, space_key=None, cql=None, include_attachments=False, ...)
            documents = reader.load_data(
                page_ids=page_ids, 
                cql=cql
            )
            
            results = []
            for doc in documents:
                results.append(DeepTutorDocument(
                    content=doc.text,
                    metadata={
                        "source": "confluence",
                        "title": doc.metadata.get("title", ""),
                        "page_id": doc.metadata.get("page_id", ""),
                        "url": doc.metadata.get("url", ""),
                        "extra": doc.metadata
                    },
                    source_id=doc.metadata.get("page_id", "unknown")
                ))
            return results
        except Exception as e:
            logger.error(f"Failed to load from Confluence: {e}")
            raise
