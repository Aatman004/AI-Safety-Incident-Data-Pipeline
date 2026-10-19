"""Base collector class for AI safety data sources."""

from abc import ABC, abstractmethod
from typing import List
from incident_pipeline.models import IncidentRecord


class BaseCollector(ABC):
    """Abstract interface for all incident and research data collectors."""

    name: str = "base"

    @abstractmethod
    def collect(self, limit: int = 25) -> List[IncidentRecord]:
        """Fetch and return normalized incident records up to the specified limit."""
        pass
