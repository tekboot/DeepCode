from typing import List, Optional
import os
import logging
from llama_index.readers.slack import SlackReader
from .base import BaseConnector, DeepTutorDocument, ConnectorFactory

logger = logging.getLogger(__name__)

@ConnectorFactory.register("slack")
class SlackConnector(BaseConnector):
    """
    Connector for Slack Workspace.
    """
    
    def __init__(self, slack_token: str = None):
        """
        Initialize Slack Connector.
        Auth: SLACK_BOT_TOKEN
        """
        self.slack_token = slack_token or os.getenv("SLACK_BOT_TOKEN")
        
        if not self.slack_token:
            logger.warning("Slack token missing.")
            
    def load_data(self, config: dict) -> List[DeepTutorDocument]:
        """
        Load messages from Slack channels.
        Config:
            - channel_ids: List of channel IDs to scrape.
        """
        channel_ids = config.get("channel_ids")
        if not channel_ids:
            # Maybe default to all? Risks hitting rate limits.
            raise ValueError("channel_ids required in config for SlackConnector")
            
        logger.info(f"Loading Slack channels: {channel_ids}")
        
        try:
            reader = SlackReader(slack_token=self.slack_token)
            documents = reader.load_data(channel_ids=channel_ids)
            
            results = []
            for doc in documents:
                results.append(DeepTutorDocument(
                    content=doc.text,
                    metadata={
                        "source": "slack",
                        "channel": doc.metadata.get("channel", "unknown"),
                        "extra": doc.metadata
                    },
                    source_id=doc.metadata.get("channel", "unknown") + "_" + str(doc.metadata.get("timestamp", ""))
                ))
            return results
        except Exception as e:
            logger.error(f"Failed to load from Slack: {e}")
            raise
