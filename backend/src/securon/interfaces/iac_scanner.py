"""IaC Scanner interfaces"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import List
from pydantic import BaseModel

from .core_types import Severity, RuleSource, RuleStatus


class SecurityRule(BaseModel):
    id: str
    name: str
    description: str
    severity: Severity
    pattern: str
    remediation: str
    source: RuleSource
    status: RuleStatus
    created_at: datetime


class ScanResult(BaseModel):
    severity: Severity
    rule_id: str
    description: str
    file_path: str
    line_number: int
    remediation: str


class IaCScanner(ABC):
    @abstractmethod
    async def scan_file(self, file_path: str) -> List[ScanResult]:
        """Scan a single Terraform file for security misconfigurations"""
        pass

    @abstractmethod
    async def scan_directory(self, directory_path: str) -> List[ScanResult]:
        """Scan a directory of Terraform files for security misconfigurations"""
        pass

    @abstractmethod
    def apply_rules(self, rules: List[SecurityRule]) -> None:
        """Apply security rules to the scanner"""
        pass