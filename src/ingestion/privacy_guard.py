from typing import List, Dict, Optional
import logging
from presidio_analyzer import AnalyzerEngine, RecognizerResult
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig
from presidio_analyzer.nlp_engine import NlpEngineProvider

logger = logging.getLogger(__name__)

class PrivacyGuard:
    """
    Local privacy shield using Microsoft Presidio to detect and scrub PII 
    from text before ingestion.
    """
    
    def __init__(self, language: str = "en", model_name: str = "en_core_web_sm"):
        self.language = language
        try:
            # Configure Presidio to use the specific spaCy model
            configuration = {
                "nlp_engine_name": "spacy",
                "models": [{"lang_code": language, "model_name": model_name}],
            }
            provider = NlpEngineProvider(nlp_configuration=configuration)
            nlp_engine = provider.create_engine()

            self.analyzer = AnalyzerEngine(nlp_engine=nlp_engine)
            self.anonymizer = AnonymizerEngine()
            logger.info(f"PrivacyGuard initialized with model: {model_name}")
        except Exception as e:
            logger.error(f"Failed to initialize Presidio: {e}")
            raise RuntimeError(f"PrivacyGuard initialization failed. Ensure '{model_name}' is installed.") from e

    def analyze(self, text: str) -> List[RecognizerResult]:
        """
        Analyze text to find PII entities.
        """
        if not text:
            return []
        
        results = self.analyzer.analyze(
            text=text,
            language=self.language,
            entities=[
                "PERSON", "PHONE_NUMBER", "EMAIL_ADDRESS", 
                "CREDIT_CARD", "CRYPTO", "IP_ADDRESS", "URL"
            ]
        )
        return results

    def anonymize(self, text: str) -> str:
        """
        Analyze and anonymize text by replacing PII with <ENTITY_TYPE>.
        """
        if not text:
            return ""

        results = self.analyze(text)
        
        # Define operators: Replace with <ENTITY_TYPE>
        operators = {
            "DEFAULT": OperatorConfig("replace", {"new_value": "<PII_REDACTED>"}),
            "PERSON": OperatorConfig("replace", {"new_value": "<PERSON>"}),
            "PHONE_NUMBER": OperatorConfig("replace", {"new_value": "<PHONE>"}),
            "EMAIL_ADDRESS": OperatorConfig("replace", {"new_value": "<EMAIL>"}),
        }

        anonymized_result = self.anonymizer.anonymize(
            text=text,
            analyzer_results=results,
            operators=operators
        )
        
        return anonymized_result.text

    def check_is_safe(self, text: str) -> bool:
        """
        Returns True if no high-confidence PII is found.
        """
        results = self.analyze(text)
        return len(results) == 0
