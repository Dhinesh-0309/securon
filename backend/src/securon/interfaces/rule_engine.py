"""Rule Engine interfaces"""

from abc import ABC, abstractmethod
from typing import List

from .iac_scanner import SecurityRule


class RuleEngine(ABC):
    @abstractmethod
    async def add_rule(self, rule: SecurityRule) -> None:
        """Add a new security rule to the engine"""
        pass

    @abstractmethod
    async def remove_rule(self, rule_id: str) -> None:
        """Remove a security rule from the engine"""
        pass

    @abstractmethod
    async def get_active_rules(self) -> List[SecurityRule]:
        """Get all active security rules"""
        pass

    @abstractmethod
    async def get_candidate_rules(self) -> List[SecurityRule]:
        """Get all candidate security rules awaiting approval"""
        pass

    @abstractmethod
    async def approve_candidate_rule(self, rule_id: str) -> None:
        """Approve a candidate rule and make it active"""
        pass

    @abstractmethod
    async def reject_candidate_rule(self, rule_id: str) -> None:
        """Reject a candidate rule"""
        pass