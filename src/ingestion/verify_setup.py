import sys
import os
import logging

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DeepTutor-Verifier")

def verify_privacy():
    logger.info("Verifying PrivacyGuard...")
    try:
        from src.ingestion.privacy_guard import PrivacyGuard
        guard = PrivacyGuard()
        
        test_text = "My name is John Doe and my email is john.doe@example.com."
        anonymized = guard.anonymize(test_text)
        
        logger.info(f"Original: {test_text}")
        logger.info(f"Anonymized: {anonymized}")
        
        if "<PERSON>" in anonymized and "<EMAIL>" in anonymized and "John Doe" not in anonymized:
            logger.info("✅ PrivacyGuard PII scrubbing working correctly.")
        else:
            logger.error("❌ PrivacyGuard failed to anonymize correctly.")
            
    except Exception as e:
        logger.error(f"❌ PrivacyGuard verification failed: {e}")

def verify_connectors():
    logger.info("Verifying Connectors...")
    try:
        from src.ingestion.connectors.base import ConnectorFactory
        from src.ingestion.connectors.github_connector import GitHubConnector
        
        # Verify Registration
        connector = ConnectorFactory.get_connector("github")
        if isinstance(connector, GitHubConnector):
            logger.info("✅ GitHubConnector registered and retrieved successfully.")
        else:
            logger.error("❌ Failed to retrieve GitHubConnector from Factory.")
            
        # Verify Jira
        from src.ingestion.connectors.jira_connector import JiraConnector
        jira = ConnectorFactory.get_connector("jira")
        if isinstance(jira, JiraConnector):
            logger.info("✅ JiraConnector registered and retrieved successfully.")
        else:
            logger.error("❌ Failed to retrieve JiraConnector.")
            
        # Verify Confluence
        from src.ingestion.connectors.confluence_connector import ConfluenceConnector
        conf = ConnectorFactory.get_connector("confluence")
        if isinstance(conf, ConfluenceConnector):
            logger.info("✅ ConfluenceConnector registered and retrieved successfully.")
        else:
            logger.error("❌ Failed to retrieve ConfluenceConnector.")
            
        # Verify Slack
        from src.ingestion.connectors.slack_connector import SlackConnector
        slack = ConnectorFactory.get_connector("slack")
        if isinstance(slack, SlackConnector):
            logger.info("✅ SlackConnector registered and retrieved successfully.")
        else:
            logger.error("❌ Failed to retrieve SlackConnector.")
            
    except Exception as e:
        logger.error(f"❌ Connector verification failed: {e}")

if __name__ == "__main__":
    verify_privacy()
    verify_connectors()
