"""ML Engine interfaces"""

from abc import ABC, abstractmethod
from typing import List
from pydantic import BaseModel

from .core_types import CloudLog, AnomalyType, AnomalyPattern, Explanation, TimeRange
from .iac_scanner import SecurityRule


class AnomalyResult(BaseModel):
    id: str
    type: AnomalyType
    severity: float
    confidence: float
    affected_resources: List[str]
    time_window: TimeRange
    patterns: List[AnomalyPattern]


class MLEngine(ABC):
    @abstractmethod
    async def process_logs(self, logs: List[CloudLog]) -> List[AnomalyResult]:
        """Process cloud logs and detect anomalies using Isolation Forest"""
        pass

    @abstractmethod
    def generate_candidate_rules(self, anomalies: List[AnomalyResult]) -> List[SecurityRule]:
        """Generate candidate security rules from detected anomalies"""
        pass

    @abstractmethod
    def explain_anomaly(self, anomaly: AnomalyResult) -> Explanation:
        """Provide detailed explanation for a detected anomaly"""
        pass