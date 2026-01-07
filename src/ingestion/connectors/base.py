from typing import List, Dict, Optional, Any
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
import datetime
import logging

logger = logging.getLogger(__name__)

@dataclass
class DeepTutorDocument:
    """
    Normalized document schema for DeepTutor.
    """
    content: str
    source_type: str  # e.g., 'github', 'jira', 'confluence'
    source_id: str    # e.g., URL, file path, ticket ID
    metadata: Dict[str, Any] = field(default_factory=dict)
    related_ids: List[str] = field(default_factory=list)
    created_at: datetime.datetime = field(default_factory=datetime.datetime.now)
    privacy_level: str = "private"  # 'public', 'private', 'internal'

class BaseConnector(ABC):
    """
    Abstract base class for all data source connectors.
    """
    
    @abstractmethod
    def load_data(self, config: Dict[str, Any]) -> List[DeepTutorDocument]:
        """
        Load data from the source and return normalized DeepTutorDocuments.
        config: Dict containing authentication and query parameters.
        """
        pass

class ConnectorFactory:
    """
    Factory to create connectors based on source type.
    """
    _connectors = {}

    @classmethod
    def register(cls, source_type: str, connector_cls=None):
        if connector_cls:
            cls._connectors[source_type] = connector_cls
            return connector_cls

        def wrapper(cls_):
            cls._connectors[source_type] = cls_
            return cls_
        return wrapper

    @classmethod
    def get_connector(cls, source_type: str) -> BaseConnector:
        connector_cls = cls._connectors.get(source_type)
        if not connector_cls:
            raise ValueError(f"No connector registered for source type: {source_type}")
        return connector_cls()
