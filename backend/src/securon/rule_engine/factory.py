"""Rule Engine factory for creating instances"""

from typing import Optional
from .engine import ConcreteRuleEngine
from ..interfaces.rule_engine import RuleEngine


def create_rule_engine(storage_path: Optional[str] = None) -> RuleEngine:
    """Create a rule engine instance with default configuration"""
    if storage_path is None:
        storage_path = "data/rules"
    
    return ConcreteRuleEngine(storage_path=storage_path)


def create_test_rule_engine() -> RuleEngine:
    """Create a rule engine instance for testing with temporary storage"""
    import tempfile
    import os
    
    temp_dir = tempfile.mkdtemp()
    return ConcreteRuleEngine(storage_path=os.path.join(temp_dir, "test_rules"))